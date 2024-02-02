import math

import psycopg2
import simplekml


def postgresql_connection():
    global connection
    host = "localhost"
    pguser = "maintenance"
    password = "parolotdb"
    db_name = "maintenance"

    connection = psycopg2.connect(
        host=host,
        user=pguser,
        password=password,
        database=db_name
    )
    connection.autocommit = True


def kmz():
    # ******************************************************************************************************************
    region = []
    site_name = []
    site_id = []
    start_lon = []
    start_lat = []
    azimutes = []
    sector = []
    site_name_for_point = []
    start_lon_for_point = []
    start_lat_for_point = []

    # ******************************************************************************************************************
    # Создаем объект KML
    kml = simplekml.Kml()

    postgresql_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT "Enodeb_name", "Longitude", "Latitude"
            FROM public."RF_Plan_LTE" group by "Enodeb_name", "Longitude", "Latitude" order by "Enodeb_name" """)
            for result in cursor.fetchall():
                site_name_for_point.append(result[0])
                start_lon_for_point.append(float(result[1]))
                start_lat_for_point.append(float(result[2]))

    except Exception as ex:
        print("[INFO] Error while working with PostgreSQL", ex)

    folder_point = kml.newfolder(name='Points')

    for shag in range(0, len(site_name_for_point)):
        description_for_point = f"""<br><br><br>
                    <table border="1" padding="0">
                      <tr><td>Site_name</td><td>{site_name_for_point[shag]}</td></tr>
                      <tr><td>Longitude</td><td>{start_lon_for_point[shag]}</td></tr>
                      <tr><td>Latitude</td><td>{start_lat_for_point[shag]}</td></tr>"""

        point = folder_point.newpoint(name=f'{site_name_for_point[shag]}', description=f'{description_for_point}',
                                      coords=[(start_lon_for_point[shag], start_lat_for_point[shag])])
        point.style.iconstyle.icon.href = 'http://www.earthpoint.us/Dots/GoogleEarth/shapes/placemark_circle.png'

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT "Region", "Enodeb_name", 
            replace(replace(replace(replace((right("Enodeb_name",6)),')',''),'G(455','455'),'_4G(1','1'),'(','') as 
            Site_id, "Longitude", "Latitude", "Azimuth", "Sector_id"
            FROM public."RF_Plan_LTE"
            where "DLEARFCN" = '1850' or "DLEARFCN" = '1857'
            order by "BTS_Name" """)
            for result in cursor.fetchall():
                region.append(result[0])
                site_name.append(result[1])
                site_id.append(result[2])
                start_lon.append(float(result[3]))
                start_lat.append(float(result[4]))
                azimutes.append(int(result[5]))
                sector.append(str(result[6][-1]).replace("4", "1").replace("5", "2")
                              .replace("6", "3").replace("7", "1").replace("8", "2")
                              .replace("9", "2"))

    except Exception as ex:
        print("[INFO] Error while working with PostgreSQL", ex)

    # ******************************************************************************************************************
    folder_point = kml.newfolder(name='Sectors')

    # Определяем вершины полигона в соответствии с азимутами
    for shag in range(0, len(site_name)):
        description_for_polygon = f"""<br><br><br>
            <table border="1" padding="0">
              <tr><td>Site id</td><td>{region[shag]}</td></tr>
              <tr><td>Site id</td><td>{site_id[shag]}</td></tr>
              <tr><td>Site_name</td><td>{site_name[shag]}</td></tr>
              <tr><td>Longitude</td><td>{start_lon[shag]}</td></tr>
              <tr><td>Latitude</td><td>{start_lat[shag]}</td></tr>
              <tr><td>Azimuth</td><td>{azimutes[shag]}</td></tr>
              <tr><td>Sector</td><td>{sector[shag]}</td></tr>"""
        polygon_name = folder_point.newpolygon(name=f"{site_name[shag]}", description=f"{description_for_polygon}")
        vertices = [(start_lon[shag], start_lat[shag])]
        for azimuth in range(azimutes[shag] - 15, azimutes[shag] + 16):
            lat = start_lat[shag] + 0.0019 * math.cos(math.radians(azimuth))
            lon = start_lon[shag] + 0.0025 * math.sin(math.radians(azimuth))
            vertices.append((lon, lat))
        polygon_name.outerboundaryis = vertices

    # Сохраняем KML файл
    kml.save("Tashkent&Tashkent_region.kml")

    # with zipfile.ZipFile("huawei.kmz", "w", compression=zipfile.ZIP_DEFLATED) as kmz:
    #     kmz.write("Tashkent&Tashkent_region.kml")


def main():
    kmz()


if __name__ == '__main__':
    main()
