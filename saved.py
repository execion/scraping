import pymysql.cursors
from os import scandir
from itertools import product
from os.path import join
from functionalities import searchNumberChapter

root = "./webnovels"
dirList = [obj.name for obj in scandir(root) if obj.is_dir()]
filesText = {}

for folder in dirList:
    tempRoute = root + "/" + folder
    filesText[folder] = [(tempRoute + "/" + obj.name) for obj in scandir(tempRoute) if obj.is_file()]

connection = pymysql.connect(
                            host="localhost",
                            user="root",
                            password="",
                            database="novel_test",
                            cursorclass=pymysql.cursors.DictCursor
                            )

with connection:
    with connection.cursor() as cursor:
        for key in filesText.keys():
            sql = "SELECT * FROM novel WHERE novel=%s;"
            cursor.execute(sql, (key))
            result = cursor.fetchall()
            if len(result) == 0:
                sql = "INSERT INTO novel(novel) VALUES(%s);"
                cursor.execute(sql, (key))
                sql = "SELECT * FROM novel WHERE novel=%s;"
                cursor.execute(sql, (key))
                result = cursor.fetchall()
            for chapter in filesText[key]:
                chapter_number = chapter.replace(".txt", "").split("/")
                chapter_number = searchNumberChapter(chapter_number[len(chapter_number) - 1])
                print(chapter)
                sql = "SELECT * FROM chapter WHERE id_novel=%s AND chapter=%s;"
                cursor.execute(sql,(result[0]["id"], chapter_number))
                if len(cursor.fetchall()) == 0:
                    sql = "INSERT INTO chapter(id_novel,chapter) VALUES(%s,%s);"
                    cursor.execute(sql, (result[0]["id"], chapter_number) )
                    sql = "SELECT id FROM chapter WHERE chapter=%s AND id_novel=%s;"
                    cursor.execute(sql,(chapter_number,result[0]["id"]))
                    id_chapter = cursor.fetchall()
                    chapterFile = open("{}".format(chapter), "r", encoding="utf-8").readlines()
                    chapterFile = [line for line in chapterFile if len(line) > 2]
                    try:
                        if len(cursor.fetchall()) == 0:
                            sql = "INSERT INTO line(id_novel, id_chapter, line) VALUES(%s,%s,%s);"
                            cursor.executemany(sql, product([result[0]["id"]],[id_chapter[0]["id"]],chapterFile))
                    except Exception:
                        print(sql)
                    connection.commit()