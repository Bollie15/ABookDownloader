import os
import json
import tkinter
import tkinter.filedialog
import getpass
import requests

session = requests.session()

COURSES_INFO_FILE = ".\\temp\\course_info.json"
DOWNLOAD_LINK = ".\\temp\\download_link.json"
USER_INFO = ".\\temp\\user_info.json"
courses_list = []
chapter_list = []

def safe_mkdir(dir_name):
    try:
        os.mkdir(str(dir_name))
    except FileExistsError:
        pass

def init():
    safe_mkdir("temp")
    safe_mkdir("Downloads")
    print("启动成功！")
    print("ABookDownloader是由HEIGE-PCloud编写的开源Abook下载软件")
    print("如果遇到任何问题，请通过https://github.com/HEIGE-PCloud/ABookDownloader 提交issue")
    print("如果这款软件帮到了您，欢迎请作者喝奶茶QwQ")

def file_window():
    tk = tkinter.Tk()
    tk.title("Choose the saving path")
    path = tkinter.StringVar()
    def selectPath():
        file_path = tkinter.filedialog.askdirectory()
        path.set(file_path)
    tkinter.Label(tk,text = "Saving Path").grid(row = 0, column = 0)
    tkinter.Entry(tk, textvariable = path).grid(row = 0, column = 1)
    tkinter.Button(tk, text = "Select", command = selectPath).grid(row = 0, column = 2)



def downloader(selected_course, selected_chapter):
    safe_mkdir(".\\Downloads\\" + selected_course['course_title'])
    safe_mkdir(".\\Downloads\\" + selected_course['course_title'] + "\\" + selected_chapter['chapter_name'])
    download_url_base = "http://abook.hep.com.cn/ICourseFiles/"
    with open(DOWNLOAD_LINK, 'r', encoding='utf-8') as courses_info:
        download_data: list = json.load(courses_info)[0]['myMobileResourceList']
    print(len(download_data), "downloadable items found!")
    for i in range(len(download_data)):
        file_name = download_data[i]['resTitle']
        file_url = download_data[i]['resFileUrl']
        print(file_name)
        url = download_url_base + file_url
        print(url)
        file_type = file_url[str(file_url).find('.'):]
        r = requests.get(url)
        location = ".\\Downloads\\" + selected_course['course_title'] + "\\" + selected_chapter['chapter_name'] + "\\" + str(file_name) + str(file_type)
        print(location)
        with open(location, "wb") as f:
            f.write(r.content)

def Abook_login(login_name, login_password):
    login_url = "http://abook.hep.com.cn/loginMobile.action"
    login_status_url = "http://abook.hep.com.cn/verifyLoginMobile.action"
    login_data = {"loginUser.loginName": login_name, "loginUser.loginPassword": login_password}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64"}
    session.post(url=login_url, data=login_data, headers=headers)
    if session.post(login_status_url).json()["message"] == "已登录":
        print("Successfully login in!")
    else:
        print("Login failed, please try again.")
        os.remove(".\\temp\\user_info.json")

def get_courses_info():
    course_info_url = "http://abook.hep.com.cn/selectMyCourseList.action?mobile=true&cur=1"
    with open(COURSES_INFO_FILE, 'w', encoding='utf-8') as file:
        json.dump(session.get(course_info_url).json(), file, ensure_ascii=False, indent=4)
    print("Courses fetched!")

def load_courses_info():
    global courses_list
    courses_list = []
    with open(COURSES_INFO_FILE, 'r', encoding='utf-8') as courses_info:
        courses_data: list = json.load(courses_info)[0]['myMobileCourseList']
        print('There are {} course(s) availaible.'.format(len(courses_data)))
        for i in range(len(courses_data)):
            course_title = eval('courses_data[{}]'.format(i))['courseTitle']
            course_id = eval('courses_data[{}]'.format(i))['courseInfoId']
            courses_list.append({'course_id': course_id, 'course_title': course_title})

def get_chapter_info(course_id):
    course_url = 'http://abook.hep.com.cn/resourceStructure.action?courseInfoId={}'.format(course_id)
    with open(".\\temp\\" + str(course_id) + '.json', 'w', encoding='utf-8') as file:
        json.dump(session.post(course_url).json(), file, ensure_ascii=False, indent=4)

def display_courses_info():
    print("0 下载全部")
    for i in range(len(courses_list)):
        print(i + 1, courses_list[i]['course_title'])
    print("o 打开下载文件夹")
    print("q 退出")

def load_chapter_info(course_id):
    global chapter_list
    chapter_list = []
    with open(".\\temp\\" + str(course_id) + '.json', 'r', encoding='utf-8') as chapter_info:
        chapter_data: list = json.load(chapter_info)
    for chapter in chapter_data:
        chapter_list.append({'chapter_id': chapter['id'], 'chapter_name': chapter['name']})

def display_chapter_info(selected_course):
    print("> " + selected_course['course_title'] + ":")
    print("0 下载全部")
    for i in range(len(chapter_list)):
        print(i + 1, chapter_list[i]['chapter_name'])
    print("q 返回上一级")

def get_download_link(course_id, chapter_id):
    download_link_url = "http://abook.hep.com.cn/courseResourceList.action?courseInfoId={}&treeId={}&cur=1".format(course_id, chapter_id)
    with open(DOWNLOAD_LINK, 'w', encoding='utf-8') as file:
        json.dump(session.get(download_link_url).json(), file, ensure_ascii=False, indent=4)

def read_login_info():
    try:
        with open(USER_INFO, 'r', encoding='utf-8') as file:
            try:
                login_info: list = json.load(file)
                return login_info
            except json.decoder.JSONDecodeError:
                return False
    except FileNotFoundError:
        return False

def write_login_info(login_name, login_password):
    with open(USER_INFO, 'w', encoding='utf-8') as file:
        json.dump({'login_name': login_name, 'login_password': login_password}, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    init()
    ### First check if there is user information stored locally.
    ###     If there is, then ask whether the user will use it or not.
    ###     If there isn't, ask user type in information directly.
    user_info = read_login_info()
    if user_info != False:
        choice = input("User {} founded! Do you want to log in as {}? (y/n) ".format(user_info['login_name'], user_info['login_name']))
        if choice == 'n':
            user_info = False
    if user_info == False:
        login_name = input("Please input login name: ")
        login_password = getpass.getpass("Please input login password: ")
        user_info = {'login_name': login_name, 'login_password': login_password}
        write_login_info(login_name, login_password)

    ### User login
    Abook_login(user_info['login_name'], user_info['login_password'])

    ### Get and load courses infomation
    get_courses_info()
    load_courses_info()

    while True:
        display_courses_info()

        
        choice = input("Enter course index to choose: ")
        try:
            choice = int(choice)
        except ValueError:
            if choice == 'o':
                os.system("explorer .\\Downloads\\")
                continue
            else:
                print("Bye~")
            break

        ### Download All!
        if choice == 0:
            for i in range(len(courses_list)):
                selected_course = courses_list[i]
                get_chapter_info(selected_course['course_id'])
                load_chapter_info(selected_course['course_id'])
                for i in range(len(chapter_list)):
                    selected_chapter = chapter_list[i]
                    get_download_link(selected_course['course_id'], selected_chapter['chapter_id'])
                    downloader(selected_course, selected_chapter)
        else:
            selected_course = courses_list[choice - 1]
            ### Get and load chapter information
            get_chapter_info(selected_course['course_id'])
            load_chapter_info(selected_course['course_id'])

            display_chapter_info(selected_course)
            try:
                choice = int(input("Enter chapter index to choose: "))
            except ValueError:
                continue
            if choice == 0:
                for i in range(len(chapter_list)):
                    selected_chapter = chapter_list[i]
                    get_download_link(selected_course['course_id'], selected_chapter['chapter_id'])
                    downloader(selected_course, selected_chapter)
            else:
                selected_chapter = chapter_list[choice - 1]
                ### Fetch the download links
                get_download_link(selected_course['course_id'], selected_chapter['chapter_id'])
                ### Download the links
                downloader(selected_course, selected_chapter)
