# -*- coding: utf-8 -*-
import cx_Oracle
import datetime
from urllib.request import urlopen
from urllib.request import HTTPError
from bs4 import BeautifulSoup
from konlpy.tag import Twitter
import re
import csv

class Clawler:
        conn = None
        cur = None
        input_word_dic = {} # input 데이터화 할 키워드 딕셔너리
        input_word_list = [] # input 데이터화 할 키워드 리스트
        input_table_counter = 0 # 오라클 DB에의 최대 속성 수 는 1,000 개 이므로 여러 개의 input 테이블이 필요함
        last_clawled_news_date = None # 실시간으로 기사를 크롤링할 때 가장 최근 작업 기사의 정보를 저장

        word_filter = ['연합뉴스', '연합인포맥스', '클릭', '채널', '구독', '저작권지',
                        '앵커', '멘트', '뉴스', '기자', '선임', '경향신문', '트위터',
                        '페이스북', '무료만화', '재', '배포', '보기', '전재', '디지털타임스',
                        '홈페이지', '바로가기', '아나운서', '매일경제', '한국경제',
                        '머니투데이', '치어리더', '레이싱걸', '한경닷텀', '글방',
                        '모바일한경', '연예뉴스', '파이낸셜뉴스', '세계일보', '경제투데이',
                        '미디어', '리포트', '국민일보', '왱', '취재', '가', '가가', '영상편집',
                        '포토', '한겨레', '절친', '신문', '애니멀', '취재', '뉴스데스크',
                        '그', '그것', '그게', '그때', '근', '기사', '기프트', '기프트카드',
                        '기프티콘', '꼬', '꼭', '꼴', '꼽', '꼽았', '꼽았다또', '꼽았습니',
                        '꽁꽁', '꽉', '꾀', '끝내', '끼', '끼리', '나', '나가야', '나도펀딩',
                        '난', '내', '내비', '누', '누가', '누구', '누군가', '뉴스스탠드', '뉴시스',
                        '다운로드', '카카오톡', '당신', '댓', '댓글', '더', '더구나', '더디',
                        '더라도', '데', '도', '도도', '도록', '독자', '돋움체', '동아', '두',
                        '뒷', '드', '디', '디다', '딘', '딥', '때', '때문', '때론', '떤',
                        '똘똘', '뚜렷', '뚜렷하', '뚝', '뜻', '띤', '라며', '렬', '렸', '렸습',
                        '롄샹', '로', '로그인', '로부터', '료', '료업', '류', '를', '리', '리가',
                        '라기', '린', '림', '마', '마는', '마음껏', '막', '만날', '만큼', '말',
                        '말로', '머니클립', '먼데이', '며', '며칠', '면서', '몇', '무', '무엇',
                        '뭔', '뭐', '및', '밑', '바', '바로', '바로가기', '박', '']

        # 오라클 데이터베이스 연동용 객체를 생성하는 메소드
        def Connect_T0_Database(self) :
            Clawler.conn = cx_Oracle.connect("Buzzbee", "Buzzbee12", "Buzzbee")
            Clawler.cur = Clawler.conn.cursor()

        # 오라클 데이터베이스 연동용 객체를 닫는 메소드
        def Close_T0_Database(self):
            Clawler.cur.close()
            Clawler.conn.close()

        # 코드를 반복적으로 실행할 때 데이터베이스 객체 명이 겹치지 않게 테이블을 삭제하는 메소드
        def Drop_Database_Table(self):
            print("****************************** drop table keyword execute* ******************************")
            sql_drop_table_article = "drop table keyword"
            self.cur.execute(sql_drop_table_article)
            print("***************************** drop table keyword complete ******************************")
            print("******************************* drop table input execute* *******************************")
            for N in range(1, Clawler.input_table_counter + 1):
                sql_drop_table_input_N = "drop table input" + str(N)
                self.cur.execute(sql_drop_table_input_N)
            print("******************************* drop table input complete ******************************")
            Clawler.input_table_counter = 0

        # 기사 단어 리스트를 저장하는 테이블 Keyword 생성 메소드
        def Create_Table_Keyword(self) :
            print("***************************** create table keyword execute *****************************")
            sql_create_table_article = "create table keyword (" \
                                       "word varchar2(30), count number(5)" \
                                       ")"
            Clawler.cur.execute(sql_create_table_article)
            print("***************************** create table keyword complete *****************************")

        # article 테이블과 input0 테이블의 레코드를 채우는 메소드(실행 초기에 원하는 학습 데이터 기간을 입력)
        def Insert_Table_Keyword(self):
            print("***************************** insert table keyword execute *****************************")
            today_date_time = datetime.datetime.now()
            today_date = today_date_time.strftime('%Y-%m-%d')
            today_year = today_date[0:4]
            today_month = today_date[5:7]
            today_day = today_date[8:10]
            print('현재 날짜 및 시간:', today_date_time)
            print('원하는 수집 기간 입력')
            print("기사 수집 시작 날짜 설정(숫자만 입력)")
            start_year = input("시작 년도: ")
            start_month = input("시작 월  : ")
            start_day = input("시작 일  : ")
            print("기사 수집 종료 날짜 설정(숫자만 입력)")
            end_year = input("종료 년도: ")
            end_month = input("종료 월  : ")
            end_day = input("종료 일  : ")
            if int(start_month) < 10:
                start_month = "0" + str(int(start_month))
            if int(start_day) < 10:
                start_day = "0" + str(int(start_day))
            if int(end_month) < 10:
                end_month = "0" + str(int(end_month))
            if int(end_day) < 10:
                end_day = "0" + str(int(end_day))
            start_date_str = start_year + "-" + start_month + "-" + start_day + " " + "00:00:00"
            end_date_str = end_year + "-" + end_month + "-" + end_day + " " + "00:00:00"
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            current_date = start_date
            while current_date <= end_date :
                current_date_str = str(current_date)
                current_year = current_date_str[0:4]
                current_month = current_date_str[5:7]
                current_day = current_date_str[8:10]
                former_top_article_oid = 0
                former_top_article_aid = 0
                current_top_article_oid = 0
                current_top_article_aid = 0
                market_start = datetime.time(9, 0, 0)
                market_end = datetime.time(15, 30, 0)
                former_input_datetime = datetime.datetime.strptime("9999-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
                page = 34
                while True :
                    '''
                    link_breaking_news_home = "http://news.naver.com/main/list.nhn?mode=LSD&amp;mid=sec&amp;sid1=001&" \
                                              "date=20171026&page=1" # 네이버 뉴스 속보 홈 주소
                    위의 네이버 뉴스 속보 홈 주소에서 data와 page만을 변경하여 각 날짜의 각 페이지에 접속할 수 있음
                    따라서 위의 날짜를 조정하면서 크롤링하여 과거의 데이터를 얻을 수 있음
                    '''
                    page += 1  # 네이버 뉴스 속보 홈에서 원하는 페이지
                    if page > 36 : break # 노트북에서는 이 이상으로 데이터를 수집하면 퍼져버려서 임시로 페이지 제한을 둠
                    link_breaking_news_home = "http://news.naver.com/main/list.nhn?mode=LSD&sid1=101&mid=sec&listType=title&" \
                                              "date=" + current_year + current_month + current_day + "&page=" + str(page)  # 네이버 뉴스 속보 홈 주소
                    print("현재 접근 링크 :", link_breaking_news_home)
                    try:
                        html_breaking_news_home = urlopen(link_breaking_news_home)
                    except HTTPError as e:
                        print(e)
                        print("\n\n\n*****오류발생 : 네이버 속보 홈페이지 link 가져오기*****\n\n\n")
                    bsObj_breaking_news_home = BeautifulSoup(html_breaking_news_home.read(), "html.parser")
                    '''
                    print("\n\n\n-----뉴스 속보 홈 html 코드-----\n\n\\n" + bsObj_breaking_news_home)
                    print("\n\n\n-----속보 기사 링크 추출-----\n\n\n")
                    print(bsObj_breaking_news_home.findAll("a", {"class":"nclicks(fls.list)"})) # 속보 기사 링크를 포함한 객체인 "a" 전체를 출력함
                    '''
                    link_test_article = bsObj_breaking_news_home.find("a", {"class": "nclicks(fls.list)"})
                    link_top_article = link_test_article.attrs['href']
                    top_article_oid = link_top_article[-18:-15]
                    top_article_aid = link_top_article[-10:]
                    current_top_article_oid = top_article_oid
                    current_top_article_aid = top_article_aid
                    if (current_top_article_oid == former_top_article_oid) and (current_top_article_aid == former_top_article_aid) :
                        break
                    former_top_article_oid = top_article_oid
                    former_top_article_aid = top_article_aid
                    for link_breaking_news_article in bsObj_breaking_news_home.findAll("a", {"class": "nclicks(fls.list)"}):
                        if 'href' in link_breaking_news_article.attrs:  # 해당 페이지 안에 있는 모든 속보 기사 링크를 첫 번째부터 마지막까지 반복적으로 출력함
                            link_one_article = link_breaking_news_article.attrs['href'] # 개별 기사의 링크
                            article_oid = link_one_article[-18:-15]
                            article_aid = link_one_article[-10:]
                            html_one_article = urlopen(link_one_article)
                            bsObj_one_article = BeautifulSoup(html_one_article.read(), "html.parser")
                            # 기사 내용에 따라(시사, 연예 등) html의 양식이 달라져 기사 제목 및 내용을 가져오지 못하는 경우가 있어서 조건문을 통해 반복적인 작업을 실행해야함
                            # 날짜 및 시간 정보를 먼저 수집해서 코드 운용시간 단축
                            date_one_article = bsObj_one_article.findAll("span", {"class": "t11"})  # 기사 날짜 가져오기(시사)
                            if str(date_one_article) == "[]":
                                date_one_article = bsObj_one_article.findAll("",{"class": "author"})  # 기사 날짜 다시 가져오기(연예)
                            if str(date_one_article) == "[]":
                                date_one_article = bsObj_one_article.find("div",{"class": "info"})  # 기사 날짜 다시 가져오기(스포츠)
                            if str(date_one_article) != "[]":
                                str_date = str(date_one_article)
                                # print(str_date)
                                refined_date = re.sub('[a-zA-Z]', '', str_date)
                                refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '',
                                                      refined_date)
                                # print(refined_date)
                                try:
                                    article_year = int(refined_date[3:7])
                                    article_month = int(refined_date[7:9])
                                    article_day = int(refined_date[9:11])
                                    article_hour = int(refined_date[12:14])
                                    article_min = int(refined_date[14:16])
                                    article_time = datetime.time(article_hour, article_min, 0)
                                except:
                                    print(refined_date, type(refined_date), '<---- 기사 날짜 및 시간 획득 오류 발생')
                                    continue
                                    '''
                                    try:
                                        print("체킹 포인트")
                                        article_year = int(refined_date[5:9])
                                        article_month = int(refined_date[9:11])
                                        article_day = int(refined_date[11:13])
                                        print("년월일 :", article_year, article_month, article_day)
                                        article_hour = int(refined_date[17:19])
                                        article_min = int(refined_date[19:21])
                                        print("시간, 분기 :", article_hour, refined_date[14:16])
                                        if refined_date[14:16] == '오후':
                                            article_hour += 12
                                        print("시분 :", article_hour, article_min)
                                        article_time = datetime.time(article_hour, article_min, 0)
                                        print(article_time)
                                    except:
                                        print(refined_date, type(refined_date), '<---- 기사 날짜 및 시간 획득 오류 발생')
                                        continue
                                    '''
                                if not (article_time >= market_start and article_time <= market_end):
                                    print(refined_date, "<---- out of market time")
                                    continue
                                else:
                                    print(refined_date)
                            else:
                                print("날짜 못받음")
                                continue
                            title_one_article = bsObj_one_article.findAll("", {"id": "articleTitle"})  # 기사 제목 가져오기(시사)
                            # date_one_article = bsObj_one_article.findAll("span", {"class": "t11"})  # 기사 날짜 가져오기(시사)
                            body_one_article = bsObj_one_article.findAll("", {"id": "articleBodyContents"})  # 기사 내용 가져오기(시사)
                            article_type = '시사'
                            if str(title_one_article) == "[]":
                                title_one_article = bsObj_one_article.findAll("", {"class": "end_tit"})  # 기사 제목 다시 가져오기(연예)
                                # date_one_article = bsObj_one_article.findAll("", {"class": "author"})  # 기사 날짜 다시 가져오기(연예)
                                body_one_article = bsObj_one_article.findAll("", {"id": "articeBody"})  # 기사 내용 다시 가져오기(연예)
                                article_type = '연예'
                            if str(title_one_article) == "[]":
                                title_one_article = bsObj_one_article.findAll("h4", {"class": "title"})  # 기사 제목 다시 가져오기(스포츠)
                                # date_one_article = bsObj_one_article.find("div", {"class": "info"})  # 기사 날짜 다시 가져오기(스포츠)
                                body_one_article = bsObj_one_article.findAll("div", {"id": "newsEndContents"})  # 기사 내용 다시 가져오기(스포츠)
                                article_type = '스포츠'
                            # 기사의 날짜 및 시간을 추출하는 작업
                            '''
                            if str(date_one_article) != "[]":
                                str_date = str(date_one_article)
                                # print(str_date)
                                refined_date = re.sub('[a-zA-Z]', '', str_date)
                                refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_date)
                                print(refined_date)
                                try:
                                    article_year = int(refined_date[3:7])
                                    article_month = int(refined_date[7:9])
                                    article_day = int(refined_date[9:11])
                                    article_hour = int(refined_date[12:14])
                                    article_min = int(refined_date[14:16])
                                    article_time = datetime.time(article_hour, article_min, 0)
                                except:
                                    print('ㄴ 기사 날짜 및 시간 획득 오류 발생\n')
                                    pass
                                if not (article_time >= market_start and article_time <= market_end):
                                    continue
                            else:
                                print("날짜 못받음")
                                continue
                            '''
                            if str(title_one_article) != "[]":
                                str_title = str(title_one_article)
                                refined_title = re.sub('[a-zA-Z]', '', str_title)
                                refined_title = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_title)
                            else:
                                print("제목 못받음")
                            if str(body_one_article) != "[]":
                                str_body = str(body_one_article)
                                # print(str_body)
                                refined_body = re.sub('[a-zA-Z]', '', str_body)
                                refined_body = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_body)
                                # print(twitter.morphs(refined_body))
                            else:
                                print("내용 못받음")
                            # 기사 속의 명사와 동사를 찾고, 이를 input_word_list에 저장하는 작업
                            twitter = Twitter()  # 명사를 추출하기 위해 KoNLPy Twitter 개체 생성
                            content = refined_title + refined_body
                            if content == None:
                                pass
                            else:
                                article_word_list = twitter.pos(content)
                                for word in article_word_list:
                                    if word[0] in Clawler.word_filter:
                                        continue
                                    if (word[1] == "Noun"): # or (word[1] == "Verb") :
                                        if not (word[0] in Clawler.input_word_dic):
                                            Clawler.input_word_dic[word[0]] = 0
                                        Clawler.input_word_dic[word[0]] += 1
                            current_input_datetime = datetime.datetime.strptime(
                                str(article_year) + "-" + str(article_month) + "-" + str(article_day) + " " \
                                + str(article_hour) + ":" + str(article_min) + ":00", "%Y-%m-%d %H:%M:%S")
                            # print('과거 vs 현재 인풋 시간 : ' + str(former_input_datetime) + ' vs ' + str(current_input_datetime))
                            former_input_datetime = current_input_datetime
                            refined_title = None
                            refined_body = None
                current_date = current_date + datetime.timedelta(days = 1)

            Clawler.input_word_list = sorted(Clawler.input_word_dic.items(), key=lambda x: x[1], reverse=True)
            Clawler.input_word_list.sort()
            for word, count in Clawler.input_word_list:
                sql_insert_table_article = "insert into keyword(" \
                                           "word, count) values (" \
                                           "\'" + word + "\', " + str(count) + \
                                           ")"
                Clawler.cur.execute(sql_insert_table_article)
            print("***************************** insert table keyword complete *****************************")

        # Keyword 테이블을 출력하는 메소드
        def Select_Table_Keyword(self):
            print("***************************** select table keyword execute *****************************")
            sql_select_table_article = "select * from keyword " \
                                       "order by count desc"
            Clawler.cur.execute(sql_select_table_article)
            record_list = Clawler.cur.fetchall()
            for word, count in record_list:
                print("{0}\t\t{1}".format(word, count))
            input_word_counter = len(Clawler.input_word_list)
            print("Input_word_list :")
            for word in Clawler.input_word_list:
                print(word[0])
            print("The number of Input column =", input_word_counter)
            print("***************************** select table keyword complete *****************************")

        # input0 테이블을 복사한 후, input 키워드 리스트를 참고하여  column을 추가하는 메소드
        def Create_Table_Input(self):
            print("****************************** create table input execute ******************************")
            if Clawler.input_table_counter == 0 :
                Clawler.input_table_counter += 1
                sql_create_table_input = "create table input" + str(Clawler.input_table_counter) + " (" \
                                           "upload_date date" \
                                           ")"
                Clawler.cur.execute(sql_create_table_input)
                print("create table input", Clawler.input_table_counter)
            for input_word in Clawler.input_word_list:
                try:
                    sql_alter_table_input_N = "alter table input" + str(Clawler.input_table_counter) + " " \
                                              "add " + input_word[0] + " number(3) default 0"
                    Clawler.cur.execute(sql_alter_table_input_N)
                except cx_Oracle.DatabaseError as e:
                    Clawler.input_table_counter += 1
                    sql_create_table_input = "create table input" + str(Clawler.input_table_counter) + " (" \
                                               "upload_date date" \
                                               ")"
                    Clawler.cur.execute(sql_create_table_input)
                    print("create table input", Clawler.input_table_counter)
                    sql_alter_table_input_N = "alter table input" + str(Clawler.input_table_counter) + " " \
                                              "add " + input_word[0] + " number(2) default 0"
                    Clawler.cur.execute(sql_alter_table_input_N)
                    continue
            print("Tne number of Input table =", Clawler.input_table_counter)
            print("****************************** create table input complete ******************************")


        # 날짜 별 input 값을 input 테이블에 저장하는 메소드
        def Insert_Table_Input(self):
            print("****************************** insert table input execute ******************************")
            today_date_time = datetime.datetime.now()
            today_date = today_date_time.strftime('%Y-%m-%d')
            today_year = today_date[0:4]
            today_month = today_date[5:7]
            today_day = today_date[8:10]
            print('현재 날짜 및 시간:', today_date_time)
            print('원하는 수집 기간 입력')
            print("기사 수집 시작 날짜 설정(숫자만 입력)")
            start_year = input("시작 년도: ")
            start_month = input("시작 월  : ")
            start_day = input("시작 일  : ")
            print("기사 수집 종료 날짜 설정(숫자만 입력)")
            end_year = input("종료 년도: ")
            end_month = input("종료 월  : ")
            end_day = input("종료 일  : ")
            if int(start_month) < 10:
                start_month = "0" + str(int(start_month))
            if int(start_day) < 10:
                start_day = "0" + str(int(start_day))
            if int(end_month) < 10:
                end_month = "0" + str(int(end_month))
            if int(end_day) < 10:
                end_day = "0" + str(int(end_day))
            start_date_str = start_year + "-" + start_month + "-" + start_day + " " + "00:00:00"
            end_date_str = end_year + "-" + end_month + "-" + end_day + " " + "00:00:00"
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            current_date = start_date
            while current_date <= end_date :
                current_date_str = str(current_date)
                current_year = current_date_str[0:4]
                current_month = current_date_str[5:7]
                current_day = current_date_str[8:10]
                former_top_article_oid = 0
                former_top_article_aid = 0
                current_top_article_oid = 0
                current_top_article_aid = 0
                market_start = datetime.time(9, 0, 0)
                market_end = datetime.time(15, 30, 0)
                former_input_datetime = datetime.datetime.strptime("9999-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
                page = 34
                while True :
                    '''
                    link_breaking_news_home = "http://news.naver.com/main/list.nhn?mode=LSD&amp;mid=sec&amp;sid1=001&" \
                                              "date=20171026&page=1" # 네이버 뉴스 속보 홈 주소
                    위의 네이버 뉴스 속보 홈 주소에서 data와 page만을 변경하여 각 날짜의 각 페이지에 접속할 수 있음
                    따라서 위의 날짜를 조정하면서 크롤링하여 과거의 데이터를 얻을 수 있음
                    '''
                    page += 1  # 네이버 뉴스 속보 홈에서 원하는 페이지
                    if page > 36 : break # 노트북에서는 이 이상으로 데이터를 수집하면 퍼져버려서 임시로 페이지 제한을 둠
                    link_breaking_news_home = "http://news.naver.com/main/list.nhn?mode=LSD&sid1=101&mid=sec&listType=title&" \
                                              "date=" + current_year + current_month + current_day + "&page=" + str(page)  # 네이버 뉴스 속보 홈 주소
                    print(link_breaking_news_home)
                    try:
                        html_breaking_news_home = urlopen(link_breaking_news_home)
                    except HTTPError as e:
                        print(e)
                        print("\n\n\n*****오류발생 : 네이버 속보 홈페이지 link 가져오기*****\n\n\n")
                    bsObj_breaking_news_home = BeautifulSoup(html_breaking_news_home.read(), "html.parser")
                    '''
                    print("\n\n\n-----뉴스 속보 홈 html 코드-----\n\n\\n" + bsObj_breaking_news_home)
                    print("\n\n\n-----속보 기사 링크 추출-----\n\n\n")
                    print(bsObj_breaking_news_home.findAll("a", {"class":"nclicks(fls.list)"})) # 속보 기사 링크를 포함한 객체인 "a" 전체를 출력함
                    '''
                    link_test_article = bsObj_breaking_news_home.find("a", {"class": "nclicks(fls.list)"})
                    link_top_article = link_test_article.attrs['href']
                    top_article_oid = link_top_article[-18:-15]
                    top_article_aid = link_top_article[-10:]
                    current_top_article_oid = top_article_oid
                    current_top_article_aid = top_article_aid
                    if (current_top_article_oid == former_top_article_oid) and (current_top_article_aid == former_top_article_aid) :
                        break
                    former_top_article_oid = top_article_oid
                    former_top_article_aid = top_article_aid
                    for link_breaking_news_article in bsObj_breaking_news_home.findAll("a", {"class": "nclicks(fls.list)"}):
                        if 'href' in link_breaking_news_article.attrs:  # 해당 페이지 안에 있는 모든 속보 기사 링크를 첫 번째부터 마지막까지 반복적으로 출력함
                            link_one_article = link_breaking_news_article.attrs['href'] # 개별 기사의 링크
                            article_oid = link_one_article[-18:-15]
                            article_aid = link_one_article[-10:]
                            html_one_article = urlopen(link_one_article)
                            bsObj_one_article = BeautifulSoup(html_one_article.read(), "html.parser")
                            # 기사 내용에 따라(시사, 연예 등) html의 양식이 달라져 기사 제목 및 내용을 가져오지 못하는 경우가 있어서 조건문을 통해 반복적인 작업을 실행해야함
                            # 날짜 및 시간 정보를 먼저 수집해서 코드 운용시간 단축
                            date_one_article = bsObj_one_article.findAll("span", {"class": "t11"})  # 기사 날짜 가져오기(시사)
                            if str(date_one_article) == "[]":
                                date_one_article = bsObj_one_article.findAll("",{"class": "author"})  # 기사 날짜 다시 가져오기(연예)
                            if str(date_one_article) == "[]":
                                date_one_article = bsObj_one_article.find("div",{"class": "info"})  # 기사 날짜 다시 가져오기(스포츠)
                            if str(date_one_article) != "[]":
                                str_date = str(date_one_article)
                                # print(str_date)
                                refined_date = re.sub('[a-zA-Z]', '', str_date)
                                refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '',
                                                      refined_date)
                                # print(refined_date)
                                try:
                                    article_year = int(refined_date[3:7])
                                    article_month = int(refined_date[7:9])
                                    article_day = int(refined_date[9:11])
                                    article_hour = int(refined_date[12:14])
                                    article_min = int(refined_date[14:16])
                                    article_time = datetime.time(article_hour, article_min, 0)
                                except:
                                    try:
                                        article_year = int(refined_date[5:9])
                                        article_month = int(refined_date[9:11])
                                        article_day = int(refined_date[11:13])
                                        article_hour = int(refined_date[17:19])
                                        article_min = int(refined_date[19:21])
                                        if refined_date[14:16] == '오후':
                                            article_hour += 12
                                        article_time = datetime.time(article_hour, article_min, 0)
                                    except:
                                        print(refined_date, '<---- 기사 날짜 및 시간 획득 오류 발생')
                                        continue
                                if not (article_time >= market_start and article_time <= market_end):
                                    print(refined_date, "<---- out of market time")
                                    continue
                                else:
                                    print(refined_date)
                            else:
                                print("날짜 못받음")
                                continue
                            title_one_article = bsObj_one_article.findAll("", {"id": "articleTitle"})  # 기사 제목 가져오기(시사)
                            # date_one_article = bsObj_one_article.findAll("span", {"class": "t11"})  # 기사 날짜 가져오기(시사)
                            body_one_article = bsObj_one_article.findAll("", {"id": "articleBodyContents"})  # 기사 내용 가져오기(시사)
                            article_type = '시사'
                            if str(title_one_article) == "[]":
                                title_one_article = bsObj_one_article.findAll("", {"class": "end_tit"})  # 기사 제목 다시 가져오기(연예)
                                # date_one_article = bsObj_one_article.findAll("", {"class": "author"})  # 기사 날짜 다시 가져오기(연예)
                                body_one_article = bsObj_one_article.findAll("", {"id": "articeBody"})  # 기사 내용 다시 가져오기(연예)
                                article_type = '연예'
                            if str(title_one_article) == "[]":
                                title_one_article = bsObj_one_article.findAll("h4", {"class": "title"})  # 기사 제목 다시 가져오기(스포츠)
                                # date_one_article = bsObj_one_article.find("div", {"class": "info"})  # 기사 날짜 다시 가져오기(스포츠)
                                body_one_article = bsObj_one_article.findAll("div", {"id": "newsEndContents"})  # 기사 내용 다시 가져오기(스포츠)
                                article_type = '스포츠'
                            # 기사의 날짜 및 시간을 추출하는 작업
                            '''
                            if str(date_one_article) != "[]":
                                str_date = str(date_one_article)
                                # print(str_date)
                                refined_date = re.sub('[a-zA-Z]', '', str_date)
                                refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_date)
                                print(refined_date)
                                try:
                                    article_year = int(refined_date[3:7])
                                    article_month = int(refined_date[7:9])
                                    article_day = int(refined_date[9:11])
                                    article_hour = int(refined_date[12:14])
                                    article_min = int(refined_date[14:16])
                                    article_time = datetime.time(article_hour, article_min, 0)
                                except:
                                    print('ㄴ 기사 날짜 및 시간 획득 오류 발생\n')
                                    pass
                                if not (article_time >= market_start and article_time <= market_end):
                                    continue
                            else:
                                print("날짜 못받음")
                                continue
                            '''
                            if str(title_one_article) != "[]":
                                str_title = str(title_one_article)
                                refined_title = re.sub('[a-zA-Z]', '', str_title)
                                refined_title = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_title)
                            else:
                                print("제목 못받음")
                            if str(body_one_article) != "[]":
                                str_body = str(body_one_article)
                                # print(str_body)
                                refined_body = re.sub('[a-zA-Z]', '', str_body)
                                refined_body = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_body)
                                # print(twitter.morphs(refined_body))
                            else:
                                print("내용 못받음")
                            # 기사 속의 명사와 동사를 찾고, 이를 input_word_list에 저장하는 작업
                            twitter = Twitter()  # 명사를 추출하기 위해 KoNLPy Twitter 개체 생성
                            article_input_dic = {}
                            content = refined_title + refined_body
                            if content == None:
                                pass
                            else:
                                article_word_list = twitter.pos(content)
                                for word in article_word_list:
                                    if (word[1] == "Noun"): # or (word[1] == "Verb") :
                                        if not (word[0] in article_input_dic):
                                            article_input_dic[word[0]] = 0
                                        article_input_dic[word[0]] += 1
                            article_input_list = sorted(article_input_dic.items(), key=lambda x: x[1], reverse=True)
                            current_input_datetime = datetime.datetime.strptime(
                                str(article_year) + "-" + str(article_month) + "-" + str(article_day) + " " \
                                + str(article_hour) + ":" + str(article_min) + ":00", "%Y-%m-%d %H:%M:%S")
                            # print('과거 vs 현재 인풋 시간 : ' + str(former_input_datetime) + ' vs ' + str(current_input_datetime))
                            if former_input_datetime != current_input_datetime:
                                former_input_datetime = current_input_datetime
                                for N in range(1, Clawler.input_table_counter + 1):
                                    sql_insert_table_input = "insert into input" + str(N) + " (upload_date) values " \
                                                               "(" + "to_date(\'" + str(article_year) + "-" \
                                                               + str(article_month) + "-" + str(article_day) + " " \
                                                               + str(article_hour) + ":" + str(article_min)\
                                                               + ":00\', \'yyyy-mm-dd hh24:mi:ss\')" \
                                                               + ")"
                                    Clawler.cur.execute(sql_insert_table_input)
                            for N in range(1, Clawler.input_table_counter + 1):
                                for word, count in article_input_list:
                                    try:
                                        sql_update_table_input_N = "update input" + str(N) + " " \
                                                                   "set " + word + " = " + word + " + " + str(count) + " " \
                                                                   "where upload_date = " + "to_date(\'" + str(current_input_datetime) \
                                                                   + "\', \'yyyy-mm-dd hh24:mi:ss\')"
                                        Clawler.cur.execute(sql_update_table_input_N)
                                    except cx_Oracle.DatabaseError as e:
                                        continue
                            refined_title = None
                            refined_body = None
                current_date = current_date + datetime.timedelta(days = 1)

            print("****************************** insert table input complete ******************************")

        # input 테이블을 출력하는 메소드
        def Select_Table_Input(self):
            print("****************************** select table input execute ******************************")
            for N in range(1, Clawler.input_table_counter + 1):
                print("select table input :" + str(N) )
                sql_select_table_input_N = "select * from input" + str(N) + " " \
                                           "order by upload_date desc"
                Clawler.cur.execute(sql_select_table_input_N)
                input_list = Clawler.cur.fetchall()
                for input in input_list:
                    print(input)
            print("****************************** select table input complete ******************************")

        # input 테이블을 return하는 메소드
        def Get_Table_Input_1(self):
            result = []
            N = 1
            print("select table input " + str(N) + " :")
            sql_select_table_input_N = "select * from input" + str(N) + " " \
                                       "order by upload_date desc"
            Clawler.cur.execute(sql_select_table_input_N)
            article_input_list = Clawler.cur.fetchall()
            for article_input in article_input_list:
                result.append(article_input)
            return result


        # input 테이블을 csv 파일로 복사하는 메소드
        def Write_CSV_Input(self):
            for N in range(1, Clawler.input_table_counter + 1):
                csv_file = open('input' + str(N) + '.csv', 'w', encoding='UTF-8')
                csv_writer = csv.writer(csv_file, delimiter=',')
                csv_attrs = ['upload_date'] + Clawler.input_word_list[(N-1)*999 : N*999] # DB 최대 컬럼 수 반영
                csv_writer.writerow(csv_attrs)
                sql_select_table_input_N = "select * from input" + str(N) + " " \
                                           "order by upload_date desc"
                Clawler.cur.execute(sql_select_table_input_N)
                article_input_list = Clawler.cur.fetchall()
                for article_input in article_input_list:
                    csv_writer.writerow(article_input)
                print("write csv input " + str(N))
                csv_file.close()

        # 실시간으로 기사를 크롤링해서 input 데이터를 얻는 메소드
        def Crawl_Realtime_news(self):
            realtime_input = []
            result_set = []
            realtime_news_count = 0
            for column in Clawler.input_word_list:
                realtime_input.append([column, 0])
            print(realtime_input) # 체크포인트
            present_datetime = datetime.datetime.now()
            present_datetime = present_datetime.replace(second = 0, microsecond = 0)
            present_datetime = datetime.datetime.strptime("2017-11-24 23:57:00", "%Y-%m-%d %H:%M:%S") # 테스트를 위해 시간을 임의로 지정
            print('현재시간 : ', present_datetime) # 체크포인트
            present_datetime_str = present_datetime.strftime('%Y-%m-%d')
            present_year = present_datetime_str[0:4]
            present_month = present_datetime_str[5:7]
            present_day = present_datetime_str[8:10]
            page = 1
            link_breaking_news_home = "http://news.naver.com/main/list.nhn?mode=LSD&sid1=101&mid=sec&listType=title&" \
                                      "date=" + present_year + present_month + present_day + "&page=" + str(page)
            print(link_breaking_news_home) # 체크포인트
            try:
                html_breaking_news_home = urlopen(link_breaking_news_home)
            except HTTPError as e:
                print(e)
                print("\n\n\n*****오류발생 : 네이버 속보 홈페이지 link 가져오기*****\n\n\n")
            bsObj_breaking_news_home = BeautifulSoup(html_breaking_news_home.read(), "html.parser")
            for link_breaking_news_article in bsObj_breaking_news_home.findAll("a", {"class": "nclicks(fls.list)"}):
                if 'href' in link_breaking_news_article.attrs:  # 해당 페이지 안에 있는 모든 속보 기사 링크를 첫 번째부터 마지막까지 반복적으로 출력함
                    link_one_article = link_breaking_news_article.attrs['href']
                    article_oid = link_one_article[-18:-15]
                    article_aid = link_one_article[-10:]
                    html_one_article = urlopen(link_one_article)
                    bsObj_one_article = BeautifulSoup(html_one_article.read(), "html.parser")
                    title_one_article = bsObj_one_article.findAll("", {"id": "articleTitle"})  # 기사 제목 가져오기
                    date_one_article = bsObj_one_article.findAll("span", {"class": "t11"})  # 기사 날짜 가져오기
                    body_one_article = bsObj_one_article.findAll("", {"id": "articleBodyContents"})  # 기사 내용 가져오기
                    if str(date_one_article) != "[]":
                        str_date = str(date_one_article)
                        refined_date = re.sub('[a-zA-Z]', '', str_date)
                        refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_date)
                        article_datetime_str = refined_date[3:7] + '-' + refined_date[7:9] + '-' + refined_date[9:11] + ' ' \
                                               + refined_date[12:14] + ':' + refined_date[14:16] + ':00'
                        article_datetime = datetime.datetime.strptime(article_datetime_str, '%Y-%m-%d %H:%M:%S')
                        print('현재 컨택한 기사 시간 : ', article_datetime) # 체크포인트
                    else:
                        print("날짜 못받음")
                    if article_datetime < present_datetime : # 무한루프를 멈추는 부분
                        print('종료시킨 기사 시간 : ', article_datetime) # 체크포인트
                        print(article_datetime < present_datetime) # 체크포인트
                        break
                    twitter = Twitter()  # 명사를 추출하기 위해 KoNLPy Twitter 개체 생성
                    if str(title_one_article) != "[]":
                        str_title = str(title_one_article)
                        refined_title = re.sub('[a-zA-Z]', '', str_title)
                        refined_title = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_title)
                    else:
                        print("제목 못받음")
                    if str(body_one_article) != "[]":
                        str_body = str(body_one_article)
                        refined_body = re.sub('[a-zA-Z]', '', str_body)
                        refined_body = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_body)
                    else:
                        print("내용 못받음")
                    # 기사 속의 명사와 동사를 찾기 위한 작업
                    twitter = Twitter()  # 명사를 추출하기 위해 KoNLPy Twitter 개체 생성
                    article_input_list = {}
                    content = refined_title + refined_body
                    if content == None:
                        pass
                    else:
                        article_word_list = twitter.pos(content)
                        for word in article_word_list:
                            if (word[1] == "Noun"):  # or (word[1] == "Verb") :
                                if not (word[0] in article_input_list):
                                    Clawler.article_input_list[word[0]] = 0
                                Clawler.article_input_list[word[0]] += 1
                    keys = sorted(article_input_list.items(), key=lambda x: x[1], reverse=True)
                    print(keys) # 체크포인트
                    for word, count in keys:
                        for input in realtime_input:
                            if word == input[0]:
                                input[1] = count
                    print(realtime_input)  # 체크포인트
                    result_set.append([])
                    for input in realtime_input:
                        result_set[realtime_news_count].append(input[1])
                    realtime_news_count += 1
                    refined_title = None
                    refined_body = None
            return (realtime_news_count, result_set)

'''
'''
'''
'''
'''
'''

# 과거 기사를 통해 학습데이터를 얻고 csv파일로 만드는 메소드 모음

clawler = Clawler()
clawler.Connect_T0_Database()

clawler.Create_Table_Keyword()
clawler.Insert_Table_Keyword()
clawler.Select_Table_Keyword()

clawler.Create_Table_Input()
clawler.Insert_Table_Input()
clawler.Select_Table_Input()
# clawler.Write_CSV_Input()

# clawler.Drop_Database_Table()
clawler.Close_T0_Database()


# 과거 기사로부터 input할 단어 리스트를 얻고, 실시간 기사를 받아 input 데이터를 얻는 메소드 모음
'''
clawler = Clawler()
clawler.Connect_T0_Database()
clawler.Create_Table_Article_N_Input_0()
clawler.Insert_Table_Article_N_Input_0()
clawler.Create_Table_Input_N()

input_list = clawler.Crawl_Realtime_news()
print('획득한 실시간 뉴스 갯수 :',input_list[0])
for n in input_list[1]:
    print(n, end = '\n')

clawler.Drop_Database_Table()
clawler.Close_Database()
'''

# 승수형 테스트 데이터를 얻는 메소드 모음(이렇게 통째로 사용하시면 되요)
'''
clawler = Clawler()
clawler.Connect_T0_Database()
clawler.Create_Table_Article_N_Input_0()
clawler.Insert_Table_Article_N_Input_0()
clawler.Create_Table_Input_N()
clawler.Insert_Table_Input_N()

result = clawler.Get_Table_Input_1()
for input in result:
    print(input, end='\n') # <- input을 다른 리스트 변수에 저장해서 리스트 사용 가능 ex) a = input -> a는 레코드를 얻습니다. (레코드 구성 : [기사날짜, 키워드1 수, 키워드2 수, ..., 마지막 키워드 수])

# clawler.Drop_Database_Table() # <- 데이터베이스를 모두 지우는 메소드
clawler.Close_Database()
'''
'''
하시다가 input 키워드가 너무 커서 줄이고 싶으시면 이 코드에서 
328번째 줄 for N in range(1, Clawler.input_table_counter + 1):
에서 Clawler.input_table_counter + 1 크기를 줄이시면 가져오는 input 테이블 수를 줄이실 수 있으세요
         --------> 그냥 N = 1 로 해서 수정했어요!!

또 특정 날짜의 기사 페이지를 임의로 설정하시고 싶으시면 이 코드에서
93번째 줄로 크롤링 시작 (페이지 -1)을 직접 설정하실 수 있으시고
102번째 줄로 크롤링 끝 페이지를 직접 설정하실 수 있으세요
'''
'''
clawler = Clawler()
clawler.Connect_T0_Database()

result = clawler.Get_Table_Input_1()
for input in result:
    print(input, end='\n')

clawler.Close_Database()
'''
