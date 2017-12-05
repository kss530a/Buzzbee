# -*- coding: utf-8 -*-
import pymysql
import datetime
from urllib.request import urlopen
from urllib.request import HTTPError
from bs4 import BeautifulSoup
from konlpy.tag import Twitter
import re
import csv
import pandas
from sklearn.cluster import  KMeans
import threading

class Crawler:
        conn = None
        cur = None
        start_page = 20
        end_page = 200
        input_Noun_list = [] # input 데이터화 할 명사 키워드 리스트
        #input_Verb_list = []  # input 데이터화 할 동사 키워드 리스트
        input_Noun_table_counter = 0 # 오라클 DB에의 최대 속성 수 는 1,000 개 이므로 여러 개의 input 테이블이 필요함
        #input_Verb_table_counter = 0  # 오라클 DB에의 최대 속성 수 는 1,000 개 이므로 여러 개의 input 테이블이 필요함
        last_crawled_news_date = None # 실시간으로 기사를 크롤링할 때 가장 최근 작업 기사의 정보를 저장
        input_cluster_dic = {} # 키워드와 클러스터 그룹을 매칭시키는 딕셔너리
        cluster_set = 4000 # 클러스터 그룹 수
        cluster_table_counter = 0 # 클러스터 테이블 수

        Noun_filter = ['플레이어', '내용', '본문', '추가', '기자', '우회', '오류', '함수', '경제', '서울', '뉴스',
                       '무단', '금지', '배포', '사업', '전재', '시장', '기업', '한국', '투자', '채널', '뉴시스',
                       '통해', '이번', '지난', '대한', '위해', '산업', '사진', '구독', '제보', '바로가기', '이후',
                       '단지', '영상', '오전', '때문', '클릭', '또한', '한편', '가운데', '에서', '여러분', '역시',
                       '오히려', '제대로', '가가', '가가린', '가가호호', '가나다', '갈랐', '갈렸', '갈렸으',
                       '것그', '것끝', '것냉', '것안', '것역', '것은', '것을윤종규', '것이므', '것일', '것임',
                       '것입', '겅솽', '게다가', '게르', '게오', '결렸다', '경젱력', '구슐', '그것', '그게',
                       '그나', '그날', '그냥', '그나', '그니', '그다음', '그녀', '그니', '그다지', '그대',
                       '그대로', '그야', '그이', '글쎄', '깊숙', '까다롭', '까다롭기', '까닭', '깜박', '깜빠',
                       '깜빡', '깜짝', '깨달', '꺄끄', '께나', '껑충', '꼬르', '꼼짝', '니니', '다가', '대낮',
                       '대표왼뽁', '더구나', '더드', '더니', '더그', '더뎌졌', '더뎌지', '더뎌질', '더디', '더딘',
                       '더라도', '더러', '더마', '더없이', '더우기', '드넒', '드넓', '드네', '드높', '드니',
                       '드디어', '뚜렷하', '뚜렷하다', '뚜렷한데', '뚜력할', '뚜렷해졌', '뚜렷해지', '뚜력해질',
                       '뚜렷했', '뚜렷했다개', '뚜렷했', '뚜렷했다', '뚫렸', '뜰근린', '뜻밖', '뜻임', '띠던',
                       '띠었', '띤다', '띤다릴', '띱니', '라든지', '마려', '마려운', '마려워', '마련돗', '머물렀',
                       '머뭇', '머쓱', '몰렸', '몰렸기', '몰렸는데', '몰렸다', '몰렸다응찰', '몰렸던', '몰렸습니',
                       '몰릴', '밝혓', '보탰다조', '보탰던', '보탰습', '보탰습니', '보탰으', '볼때', '빚던',
                       '빚어', '빚어온', '빚어질', '빚었', '빚었는데', '빚었다', '빚었던', '빚으', '빚진', '빠듯',
                       '빠듯하', '빳빳하', '뽑내', '뽑낸', '뽐냈으', '뽀얀', '뽀얗', '뽐내', '뽑낸', '뽑냈으',
                       '뿌연', '뿌옇', '뿐더러', '뿜어', '뿜어내', '뿜어져', '삐걱', '삐끗', '삑삑', '성큼',
                       '성큼성큼', '송출뿐', '시큰둥', '시큰둥합니', '시킴', '실었다문', '실었습니', '심심찮',
                       '쏜다', '쏠렸', '쏠렸는데', '쏠렸던', '쏠리', '쏠린', '쏠릴' ,'쏠림시', '쑤시거', '어디',
                       '어디가', '어딘', '어딘가', '어어', '어엿', '어요', '어우러', '어우러져', '어우러지',
                       '어우러진', '어우러질', '억워늘', '없다보닌', '없다릴', '엊그제', '엎친', '엎친데', '우스',
                       '일쑤', '일컫', '일컫는', '일컫는다', '일컫는다또', '일컫는다이같', '일컫는데', '일컫습니',
                       '일컬', '일컬어', '있다김윤림', '있다꼬북칩', '있다쇼룸', '있다앱콘텍', '있다예컨데',
                       '있다위츠뷰', '있다유혜승', '있다윤종규', '있다임혜선', '있다천혜', '있다틱',
                       '있다팬시컷트', '있다펫', '있다플런티', '있다혁단협', '있엇습니', '잠깐', '저쪽', '젓득층',
                       '주메', '주무르', '짊어져', '짊어지', '짊어질', '쪼개', '쪼개듯', '쪼개어', '쪼갤', '쪼그',
                       '쪼그라들', '쪼이', '쪼인', '차라', '차라리', '참으로', '']

        Verb_filter = []

        v1 = ['가거', '가게', '가겠', '가고', '가구', '가기', '가긴', '가길'] # 가다
        v2 = ['가까워져', '가짜워졌', '가까워지', '가까워지는', '가까워진', '가까워질'] # 가깝다
        v3 = ['가꾸고', '가꾸기', '가꾸는', '가꾸며', '가꾸세', '가꾸어', '가꿀', '가꿔'] # 가꾸다
        v4 = ['가네', '가느', '가는', '가니', '가다', '가더', '가던', '가도', '가며', '가서', '가실', '가야',
              '가자'] # 가다
        v5 = ['가능해져', '가능해졌', '가능해지', '가능해지는', '가능해진', '가능해질', '가능해짐', '가능해집니'] # 가능하다
        v6 = ['가라앉', '', '', '', '', '']  # 가라앉다
        v7 = ['가려', '가려져', '가려졌', '가려지', '가린', '가릴'] # 가리다
        v8 = ['가로막', '', '', '', '', '', '', '', '', ''] # 가로막다
        v9 = ['가르', '가르는', '가른', '가를', '가린', '가릴', '', '', '', ''] # 가르다
        v10 = ['가르쳐', '가르쳤', '가르치', '가르치는', '가르친', '', '', '', '', ''] # 가르치다
        v11 = ['가리', '가리는', '가린', '가릴', '', '', '', '', '', ''] # 가리다
        v12 = ['가리켰', '가리키', '가리키는', '가리킨', '', '', '', '', '', ''] # 가리키다
        v13 = ['가보겠', '가보고', '가보니', '가보다', '가보려', '가보면', '기보지', '가본', '가볼', '가봐', '가봤'] # 가보다
        v14 = ['가입하거', '가입하게', '가입하고', '가입하기', '가입하느', '가입하는', '가입하더', '가입하더',
              '가입하도', '가입하려', '가입하며', '가입하면', '가입하세', '가입하셔', '가입하시', '가입하신',
              '가입하실', '가입하여', '가입하자', '가입하지', '가입한', '가입할', '가입해', '가입해도', '가입해야',
              '가입했'] # 가입하다
        v15 = ['가잖', '', '', '', '', '', '', '', '', ''] # 가잖다
        v16 = ['가져', '가져가', '가져가게', '가져가고', '가져가기', '가져가느', '가져가는', '가져가려', '가져가며',
              '가져가면', '가져가실', '가져가야', '가져가지', '가져간', '가져갈'] # 가져가다
        v17 = ['가져다주진', '가져다준', '가져다줬'] # 가져다주다
        v18 = ['가져오', '가져오겠', '가져오고', '가져오기', '가져오는', '가져오며', '가져오면', '가져오지', '가져오진',
              '가져온', '가져올', '가져와', '가져왔'] # 가져오다
        v19 = ['가졌', '가지', '가지는', '가지니', '가진', '가질', '', '', '', ''] # 가지다
        v20 = ['가하거', '가하게', '가하겠', '가하고', '가하기', '가하는', '가하더', '가하려', '가하며', '가하지',
              '가한', '가할', '가합', '가해', '가해야', '가했'] # 가하다
        v21 = ['갇혀', '갇혔', '갇히', '갇힌', '', '', '', '', '', ''] # 갇히다
        v22 = ['갈려', '', '', '', '', '', '', '', '', ''] # 갈리다
        v23 = ['', '', '', '', '', '', '', '', '', '']
        v24 = ['', '', '', '', '', '', '', '', '', '']

        def Store_Crawler(self):
            print("****************************** store crawler info execute *******************************")
            try:
                sql_create_table_info = "create table info (" \
                                        "input_Noun_table_counter smallint, cluster_set smallint, cluster_table_counter smallint" \
                                        ")"
                self.cur.execute(sql_create_table_info)
                sql_insert_table_info = "insert into info (input_Noun_table_counter, cluster_set, cluster_table_counter) values " \
                                        "("+ str(self.input_Noun_table_counter) + ", " + str(self.cluster_set) +", " + str(self.cluster_table_counter) +")"
                self.cur.execute(sql_insert_table_info)
                self.conn.commit()
            except:
                sql_drop_table_info = "drop table info"
                self.cur.execute(sql_drop_table_info)
                sql_create_table_info = "create table info (" \
                                        "input_Noun_table_counter smallint, cluster_set smallint, cluster_table_counter smallint" \
                                        ")"
                self.cur.execute(sql_create_table_info)
                sql_insert_table_info = "insert into info (input_Noun_table_counter, cluster_set, cluster_table_counter) values " \
                                        "(" + str(self.input_Noun_table_counter) + ", " + str(self.cluster_set) + ", " + str(self.cluster_table_counter) + ")"
                self.cur.execute(sql_insert_table_info)
                self.conn.commit()
            print("***************************** store crawler info complete ******************************")

        def Set_Up_Crawler(self):
            print("***************************** set up crawler info execute ******************************")
            try:
                sql_select_table_info = "select input_Noun_table_counter, cluster_set, cluster_table_counter from info"
                self.cur.execute(sql_select_table_info)
                info_list = self.cur.fetchall()
                for input_Noun_table_counter, cluster_set, cluster_table_counter in info_list:
                    self.input_Noun_table_counter = input_Noun_table_counter
                    self.cluster_set = cluster_set
                    self.cluster_table_counter = cluster_table_counter
                print("input_Noun_table_counter =", self.input_Noun_table_counter)
                print("cluster_set =", self.cluster_set)
                print("cluster_table_counter =", self.cluster_table_counter)
            except:
                print("이전에 실행했던 Crawler의 정보가 없습니다.")
                pass
            try:
                sql_select_table_keyword = "select * from keyword_Noun " \
                                           "order by count desc"
                self.cur.execute(sql_select_table_keyword)
                record_list = self.cur.fetchall()
                for word, count, cluster in record_list:
                    self.input_Noun_list.append(word)
                    self.input_cluster_dic[word] = cluster
                self.input_Noun_list.sort()
                print("input_Noun_list =", self.input_Noun_list)
                print("matching keyword and cluster_id success")
            except:
                print("keyword_Noun table의 정보를 받지 못했습니다.")
            print("***************************** set up crawler info complete ******************************")

        # 오라클 데이터베이스 연동용 객체를 생성하는 메소드
        def Connect_To_Database(self) :
            print("***************************** connect to database execute ******************************")
            self.conn = pymysql.connect(host='localhost',user='seungsu',password='tmdtn12',
                                        db='seungsu', charset='utf8')
            self.cur = self.conn.cursor()
            print("***************************** connect to database complete ******************************")

        # 오라클 데이터베이스 연동용 객체를 닫는 메소드
        def Close_To_Database(self):
            print("****************************** close to database execute *******************************")
            self.cur.close()
            self.conn.close()
            print("****************************** close to database complete *******************************")

        # 코드를 반복적으로 실행할 때 데이터베이스 객체 명이 겹치지 않게 테이블을 삭제하는 메소드
        def Drop_Database_Table_Keyword(self):
            print("****************************** drop table keyword execute *******************************")
            sql_drop_table_keyword = "drop table keyword_Noun"
            self.cur.execute(sql_drop_table_keyword)
            '''
            sql_drop_table_keyword = "drop table keyword_Verb"
            self.cur.execute(sql_drop_table_keyword)
            '''
            print("***************************** drop table keyword complete ******************************")

        def Drop_Database_Table_Input(self):
            print("******************************* drop table input execute ********************************")
            if self.input_Noun_table_counter != 0:
                for N in range(1, self.input_Noun_table_counter + 1):
                    sql_drop_table_input = "drop table input_Noun" + str(N)
                    self.cur.execute(sql_drop_table_input)
            '''
            if self.input_Verb_table_counter != 0:
                for N in range(1, self.input_Verb_table_counter + 1):
                    sql_drop_table_input = "drop table input_Verb" + str(N)
                    self.cur.execute(sql_drop_table_input)
            '''
            self.input_Noun_table_counter = 0
            self.input_Verb_table_counter = 0
            print("******************************* drop table input complete ******************************")

        def Drop_Database_Table_Cluster(self):
            print("****************************** drop table cluster execute *******************************")
            if self.cluster_table_counter != 0:
                for N in range(1, self.cluster_table_counter + 1):
                    sql_drop_table_cluster = "drop table cluster_Noun" + str(N)
                    self.cur.execute(sql_drop_table_cluster)
            '''
            if self.input_Verb_table_counter != 0:
                for N in range(1, self.input_Verb_table_counter + 1):
                    sql_drop_table_input = "drop table input_Verb" + str(N)
                    self.cur.execute(sql_drop_table_input)
            '''
            self.input_table_counter = 0
            #self.input_Verb_table_counter = 0
            print("****************************** drop table cluster complete *****************************")

        # 기사 단어 리스트를 저장하는 테이블 Keyword 생성 메소드
        def Create_Table_Keyword(self) :
            print("***************************** create table keyword execute *****************************")
            sql_create_table_keyword = "create table keyword_Noun (" \
                                       "word varchar(30), count smallint, cluster_id smallint" \
                                       ")"
            self.cur.execute(sql_create_table_keyword)
            '''
            sql_create_table_keyword = "create table keyword_Verb (" \
                                       "word varchar(30), count smallint, cluster_id smallint" \
                                       ")"
            self.cur.execute(sql_create_table_keyword)
            '''
            print("***************************** create table keyword complete *****************************")

        # article 테이블과 input0 테이블의 레코드를 채우는 메소드(실행 초기에 원하는 학습 데이터 기간을 입력)
        def Insert_Table_Keyword(self):
            print("***************************** insert table keyword execute *****************************")
            print('학습에 사용할 키워드를 추출할 기간을 정해주세요.')
            today_date_time = datetime.datetime.now()
            today_date = today_date_time.strftime('%Y-%m-%d')
            today_year = today_date[0:4]
            today_month = today_date[5:7]
            today_day = today_date[8:10]
            print('현재 날짜 및 시간:', today_date_time)
            print('원하는 수집 기간 입력')
            print("기사 수집 시작 날짜 설정(숫자만 입력)")
            start_year = 2017#input("시작 년도: ")
            start_month = 11#input("시작 월  : ")
            start_day = 28#input("시작 일  : ")
            print("기사 수집 종료 날짜 설정(숫자만 입력)")
            end_year = 2017#input("종료 년도: ")
            end_month = 12#input("종료 월  : ")
            end_day = 4#input("종료 일  : ")
            if int(start_month) < 10:
                start_month = "0" + str(int(start_month))
            if int(start_day) < 10:
                start_day = "0" + str(int(start_day))
            if int(end_month) < 10:
                end_month = "0" + str(int(end_month))
            if int(end_day) < 10:
                end_day = "0" + str(int(end_day))
            start_date_str = str(start_year) + "-" + str(start_month) + "-" + str(start_day) + " " + "00:00:00"
            end_date_str = str(end_year) + "-" + str(end_month) + "-" + str(end_day) + " " + "00:00:00"
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            current_date = start_date
            keyword_Noun_dic = {}
            keyword_Verb_dic = {}
            while current_date <= end_date :
                if current_date.weekday() > 4: # 주식시장은 평일에만 개장하기 때문에 주일, 주말의 기사는 제외함
                    current_date = current_date + datetime.timedelta(days=1)
                    continue
                current_date_str = str(current_date)
                current_year = current_date_str[0:4]
                current_month = current_date_str[5:7]
                current_day = current_date_str[8:10]
                market_start = datetime.time(9, 0, 0)
                market_end = datetime.time(15, 30, 0)
                extend_market_end = datetime.time(15, 35, 0)
                former_input_datetime = datetime.datetime.strptime("9999-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
                page = self.start_page
                while True :
                    '''
                    link_breaking_news_home = "http://news.naver.com/main/list.nhn?mode=LSD&amp;mid=sec&amp;sid1=001&" \
                                              "date=20171026&page=1" # 네이버 뉴스 속보 홈 주소
                    위의 네이버 뉴스 속보 홈 주소에서 data와 page만을 변경하여 각 날짜의 각 페이지에 접속할 수 있음
                    따라서 위의 날짜를 조정하면서 크롤링하여 과거의 데이터를 얻을 수 있음
                    '''
                    page += 1  # 네이버 뉴스 속보 홈에서 원하는 페이지
                    if page > self.end_page : break # 노트북에서는 이 이상으로 데이터를 수집하면 퍼져버려서 임시로 페이지 제한을 둠
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
                    link_sample_article = link_test_article.attrs['href']  # 개별 기사의 링크
                    html_sample_article = urlopen(link_sample_article)
                    bsObj_sample_article = BeautifulSoup(html_sample_article.read(), "html.parser")
                    # 기사 내용에 따라(시사, 연예 등) html의 양식이 달라져 기사 제목 및 내용을 가져오지 못하는 경우가 있어서 조건문을 통해 반복적인 작업을 실행해야함
                    # 날짜 및 시간 정보를 먼저 수집해서 코드 운용시간 단축
                    date_sample_article = bsObj_sample_article.findAll("span", {"class": "t11"})  # 기사 날짜 가져오기(시사)
                    if str(date_sample_article) == "[]":
                        date_sample_article = bsObj_sample_article.findAll("", {"class": "author"})  # 기사 날짜 다시 가져오기(연예)
                    if str(date_sample_article) == "[]":
                        date_sample_article = bsObj_sample_article.find("div", {"class": "info"})  # 기사 날짜 다시 가져오기(스포츠)
                    if str(date_sample_article) != "[]":
                        str_date = str(date_sample_article)
                        # print(str_date)
                        refined_date = re.sub('[a-zA-Z]', '', str_date)
                        refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_date)
                        # print(refined_date)
                        try:
                            article_year = int(refined_date[3:7])
                            article_month = int(refined_date[7:9])
                            article_day = int(refined_date[9:11])
                            article_hour = int(refined_date[12:14])
                            article_min = int(refined_date[14:16])
                            print(article_year, article_month, article_day, article_hour, article_min)
                            article_time = datetime.time(article_hour, article_min, 0)
                        except:
                            print(refined_date, type(refined_date), '<---- 기사 날짜 및 시간 획득 오류 발생')
                            pass
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
                        try:
                            if article_time > extend_market_end:
                                print(refined_date, "<---- skip page")
                                continue
                            elif article_time < market_start:
                                break
                            else:
                                print(refined_date, "<---- 접근 페이지 첫번째 기사 날짜 및 시간")
                        except:
                            pass
                    else:
                        print("날짜 및 시간 못받음")
                        pass
                    for link_breaking_news_article in bsObj_breaking_news_home.findAll("a", {"class": "nclicks(fls.list)"}):
                        if 'href' in link_breaking_news_article.attrs:  # 해당 페이지 안에 있는 모든 속보 기사 링크를 첫 번째부터 마지막까지 반복적으로 출력함
                            link_one_article = link_breaking_news_article.attrs['href'] # 개별 기사의 링크
                            html_one_article = urlopen(link_one_article)
                            try:
                                bsObj_one_article = BeautifulSoup(html_one_article.read(), "html.parser")
                            except:
                                continue
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
                                    continue
                                if not (article_time >= market_start and article_time <= market_end):
                                    print(refined_date, "<---- out of market time")
                                    continue
                                else:
                                    print(refined_date, "<---- 접근 기사 날짜 및 시간")
                            else:
                                print("날짜 및 시간 못받음")
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
                                    if len(word[0]) <= 1:
                                        continue
                                    if word[0] in Crawler.Noun_filter:
                                        continue
                                    if word[0] in Crawler.Verb_filter:
                                        continue
                                    if (word[1] == "Noun"):
                                        if not (word[0] in keyword_Noun_dic):
                                            keyword_Noun_dic[word[0]] = 0
                                        keyword_Noun_dic[word[0]] += 1
                                    if (word[1] == "Verb"):
                                        if not (word[0] in keyword_Verb_dic):
                                            keyword_Verb_dic[word[0]] = 0
                                        keyword_Verb_dic[word[0]] += 1
                            current_input_datetime = datetime.datetime.strptime(
                                str(article_year) + "-" + str(article_month) + "-" + str(article_day) + " " \
                                + str(article_hour) + ":" + str(article_min) + ":00", "%Y-%m-%d %H:%M:%S")
                            # print('과거 vs 현재 인풋 시간 : ' + str(former_input_datetime) + ' vs ' + str(current_input_datetime))
                            former_input_datetime = current_input_datetime
                            refined_title = None
                            refined_body = None
                current_date = current_date + datetime.timedelta(days = 1)

            Noun_list = sorted(keyword_Noun_dic.items(), key=lambda x: x[1], reverse=True)
            Noun_list.sort()
            for word, count in Noun_list:
                if count < 10: # 등장 횟수가 지나치게 적은 단어는 제한
                    continue
                sql_insert_table_keyword = "insert into keyword_Noun(" \
                                           "word, count, cluster_id) values ('" \
                                           + word + "', " + str(count) + ", 0"\
                                           ")"
                self.cur.execute(sql_insert_table_keyword)
                self.conn.commit()
            sql_select_table_keyword = "select * from keyword_Noun " \
                                       "order by count desc"
            self.cur.execute(sql_select_table_keyword)
            record_list = self.cur.fetchall()
            for word, count, cluster in record_list:
                self.input_Noun_list.append(word)
            self.input_Noun_list.sort()
            input_Noun_counter = len(self.input_Noun_list)
            print("Input_Noun_list =", self.input_Noun_list)
            print("The number of Input Noun column =", input_Noun_counter)
            '''
            Verb_list = sorted(keyword_Verb_dic.items(), key=lambda x: x[1], reverse=True)
            Verb_list.sort()
            for word, count in Verb_list:
                sql_insert_table_keyword = "insert into keyword_Verb(" \
                                           "word, count, cluster_id) values (" \
                                           + word + ", " + str(count) + ", 0"\
                                           ")"
                self.cur.execute(sql_insert_table_keyword)
                self.conn.commit()
            sql_select_table_keyword = "select * from keyword_Verb " \
                                       "order by count desc"
            self.cur.execute(sql_select_table_keyword)
            record_list = self.cur.fetchall()
            for word, count, cluster in record_list:
                self.input_Verb_list.append(word)
            self.input_Verb_list.sort()
            input_Verb_counter = len(self.input_Verb_list)
            print("Input_Verb_list =", self.input_Verb_list)
            print("The number of Input Verb column =", input_Verb_counter)
            '''
            print("***************************** insert table keyword complete *****************************")

        # Keyword 테이블을 출력하는 메소드
        def Select_Table_Keyword(self):
            print("***************************** select table keyword execute *****************************")
            sql_select_table_keyword = "select * from keyword_Noun " \
                                       "order by count desc"
            self.cur.execute(sql_select_table_keyword)
            record_list = self.cur.fetchall()
            for word, count, cluster in record_list:
                print("{0}\t\t{1}".format(word, count))
            '''
            sql_select_table_keyword = "select * from keyword_Verb " \
                                       "order by count desc"
            self.cur.execute(sql_select_table_keyword)
            record_list = self.cur.fetchall()
            for word, count, cluster in record_list:
                print("{0}\t\t{1}".format(word, count))
            '''
            print("***************************** select table keyword complete *****************************")

        # input0 테이블을 복사한 후, input 키워드 리스트를 참고하여  column을 추가하는 메소드
        def Create_Table_Input(self):
            print("****************************** create table input execute ******************************")
            if self.input_Noun_table_counter == 0 :
                self.input_Noun_table_counter += 1
                sql_create_table_input = "create table input_Noun" + str(self.input_Noun_table_counter) + " (" \
                                           "upload_date datetime" \
                                           ")"
                self.cur.execute(sql_create_table_input)

                print("create table input_Noun", self.input_Noun_table_counter)
            for input_word in self.input_Noun_list:
                try:
                    sql_alter_table_input = "alter table input_Noun" + str(self.input_Noun_table_counter) + " " \
                                              "add " + input_word + " smallint default 0"
                    self.cur.execute(sql_alter_table_input)

                except:
                    self.input_Noun_table_counter += 1
                    sql_create_table_input = "create table input_Noun" + str(self.input_Noun_table_counter) + " (" \
                                               "upload_date datetime" \
                                               ")"
                    self.cur.execute(sql_create_table_input)
                    self.conn.commit()
                    print("create table input_Noun", self.input_Noun_table_counter)
                    sql_alter_table_input = "alter table input_Noun" + str(self.input_Noun_table_counter) + " " \
                                              "add " + input_word + " smallint default 0"
                    self.cur.execute(sql_alter_table_input)

                    continue
            print("Tne number of Input Noun table =", self.input_Noun_table_counter)
            '''
            if self.input_Verb_table_counter == 0 :
                self.input_Verb_table_counter += 1
                sql_create_table_input = "create table input_Verb" + str(self.input_Verb_table_counter) + " (" \
                                           "upload_date datetime" \
                                           ")"
                self.cur.execute(sql_create_table_input)

                print("create table input_Verb", self.input_Verb_table_counter)
            for input_word in self.input_Verb_list:
                try:
                    sql_alter_table_input = "alter table input_Verb" + str(self.input_Verb_table_counter) + " " \
                                              "add " + input_word + " smallint default 0"
                    self.cur.execute(sql_alter_table_input)

                except cx_Oracle.DatabaseError as e:
                    self.input_Verb_table_counter += 1
                    sql_create_table_input = "create table input_Verb" + str(self.input_Verb_table_counter) + " (" \
                                               "upload_date datetime" \
                                               ")"
                    self.cur.execute(sql_create_table_input)

                    print("create table input_Verb", self.input_Verb_table_counter)
                    sql_alter_table_input = "alter table input_Verb" + str(self.input_Verb_table_counter) + " " \
                                              "add " + input_word + " smallint default 0"
                    self.cur.execute(sql_alter_table_input)

                    continue
            print("The number of Input Verb table =", self.input_Verb_table_counter)
            '''
            print("****************************** create table input complete ******************************")


        # 날짜 별 input 값을 input 테이블에 저장하는 메소드
        def Insert_Table_Input(self):
            print("****************************** insert table input execute ******************************")
            print("수집한 키워드와 매칭시킬 기사를 추출할 기간을 정해주세요.")
            today_date_time = datetime.datetime.now()
            today_date = today_date_time.strftime('%Y-%m-%d')
            today_year = today_date[0:4]
            today_month = today_date[5:7]
            today_day = today_date[8:10]
            print('현재 날짜 및 시간:', today_date_time)
            print('원하는 수집 기간 입력')
            print("기사 수집 시작 날짜 설정(숫자만 입력)")
            start_year = 2017#input("시작 년도: ")
            start_month = 11#input("시작 월  : ")
            start_day = 28#input("시작 일  : ")
            print("기사 수집 종료 날짜 설정(숫자만 입력)")
            end_year = 2017#input("종료 년도: ")
            end_month = 12#input("종료 월  : ")
            end_day = 4#input("종료 일  : ")
            if int(start_month) < 10:
                start_month = "0" + str(int(start_month))
            if int(start_day) < 10:
                start_day = "0" + str(int(start_day))
            if int(end_month) < 10:
                end_month = "0" + str(int(end_month))
            if int(end_day) < 10:
                end_day = "0" + str(int(end_day))
            start_date_str = str(start_year) + "-" + str(start_month) + "-" + str(start_day) + " " + "00:00:00"
            end_date_str = str(end_year) + "-" + str(end_month) + "-" + str(end_day) + " " + "00:00:00"
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            current_date = start_date
            while current_date <= end_date :
                if current_date.weekday() > 4: # 주식시장은 평일에만 개장하기 때문에 주일, 주말의 기사는 제외함
                    current_date = current_date + datetime.timedelta(days=1)
                    continue
                current_date_str = str(current_date)
                current_year = current_date_str[0:4]
                current_month = current_date_str[5:7]
                current_day = current_date_str[8:10]
                market_start = datetime.time(9, 0, 0)
                market_end = datetime.time(15, 30, 0)
                extend_market_end = datetime.time(15, 35, 0)
                former_input_datetime = datetime.datetime.strptime("9999-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
                page = self.start_page
                while True :
                    '''
                    link_breaking_news_home = "http://news.naver.com/main/list.nhn?mode=LSD&amp;mid=sec&amp;sid1=001&" \
                                              "date=20171026&page=1" # 네이버 뉴스 속보 홈 주소
                    위의 네이버 뉴스 속보 홈 주소에서 data와 page만을 변경하여 각 날짜의 각 페이지에 접속할 수 있음
                    따라서 위의 날짜를 조정하면서 크롤링하여 과거의 데이터를 얻을 수 있음
                    '''
                    page += 1  # 네이버 뉴스 속보 홈에서 원하는 페이지
                    if page > self.end_page : break # 노트북에서는 이 이상으로 데이터를 수집하면 퍼져버려서 임시로 페이지 제한을 둠
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
                    link_sample_article = link_test_article.attrs['href']  # 개별 기사의 링크
                    html_sample_article = urlopen(link_sample_article)
                    bsObj_sample_article = BeautifulSoup(html_sample_article.read(), "html.parser")
                    # 기사 내용에 따라(시사, 연예 등) html의 양식이 달라져 기사 제목 및 내용을 가져오지 못하는 경우가 있어서 조건문을 통해 반복적인 작업을 실행해야함
                    # 날짜 및 시간 정보를 먼저 수집해서 코드 운용시간 단축
                    date_sample_article = bsObj_sample_article.findAll("span", {"class": "t11"})  # 기사 날짜 가져오기(시사)
                    if str(date_sample_article) == "[]":
                        date_sample_article = bsObj_sample_article.findAll("", {"class": "author"})  # 기사 날짜 다시 가져오기(연예)
                    if str(date_sample_article) == "[]":
                        date_sample_article = bsObj_sample_article.find("div", {"class": "info"})  # 기사 날짜 다시 가져오기(스포츠)
                    if str(date_sample_article) != "[]":
                        str_date = str(date_sample_article)
                        # print(str_date)
                        refined_date = re.sub('[a-zA-Z]', '', str_date)
                        refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_date)
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
                            pass
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
                        try:
                            if article_time > extend_market_end:
                                print(refined_date, "<---- skip page")
                                continue
                            elif article_time < market_start:
                                break
                            else:
                                print(refined_date, "<---- 접근 페이지 첫번째 기사 날짜 및 시간")
                        except:
                            pass
                    else:
                        print("날짜 및 시간 못받음")
                        pass
                    for link_breaking_news_article in bsObj_breaking_news_home.findAll("a", {"class": "nclicks(fls.list)"}):
                        if 'href' in link_breaking_news_article.attrs:  # 해당 페이지 안에 있는 모든 속보 기사 링크를 첫 번째부터 마지막까지 반복적으로 출력함
                            link_one_article = link_breaking_news_article.attrs['href'] # 개별 기사의 링크
                            article_oid = link_one_article[-18:-15]
                            article_aid = link_one_article[-10:]
                            html_one_article = urlopen(link_one_article)
                            try:
                                bsObj_one_article = BeautifulSoup(html_one_article.read(), "html.parser")
                            except:
                                continue
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
                                refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_date)
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
                                    continue
                                if not (article_time >= market_start and article_time <= market_end):
                                    print(refined_date, "<---- out of market time")
                                    continue
                                else:
                                    print(refined_date, "<---- 접근 기사 날짜 및 시간")
                            else:
                                print("날짜 및 시간 못받음")
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
                            article_input_Noun_dic = {}
                            article_input_Verb_dic = {}
                            content = refined_title + refined_body
                            if content == None:
                                pass
                            else:
                                article_word_list = twitter.pos(content)
                                for word in article_word_list:
                                    if len(word[0]) <= 1:
                                        continue
                                    if word[0] in Crawler.Noun_filter:
                                        continue
                                    if word[0] in Crawler.Verb_filter:
                                        continue
                                    if (word[1] == "Noun"):
                                        if not (word[0] in article_input_Noun_dic):
                                            article_input_Noun_dic[word[0]] = 0
                                        article_input_Noun_dic[word[0]] += 1
                                    if (word[1] == "Verb"):
                                        if not (word[0] in article_input_Verb_dic):
                                            article_input_Verb_dic[word[0]] = 0
                                        article_input_Verb_dic[word[0]] += 1
                            article_input_Noun_list = sorted(article_input_Noun_dic.items(), key=lambda x: x[1], reverse=True)
                            article_input_Verb_list = sorted(article_input_Verb_dic.items(), key=lambda x: x[1], reverse=True)
                            current_input_datetime = datetime.datetime.strptime(
                                str(article_year) + "-" + str(article_month) + "-" + str(article_day) + " " \
                                + str(article_hour) + ":" + str(article_min) + ":00", "%Y-%m-%d %H:%M:%S")
                            # print('과거 vs 현재 인풋 시간 : ' + str(former_input_datetime) + ' vs ' + str(current_input_datetime))
                            if former_input_datetime != current_input_datetime:
                                former_input_datetime = current_input_datetime
                                for N in range(1, self.input_Noun_table_counter + 1):
                                    sql_insert_table_input = "insert into input_Noun" + str(N) + " (upload_date) values " \
                                                               "(" + "str_to_date('" + str(article_year) + "-" \
                                                               + str(article_month) + "-" + str(article_day) + " " \
                                                               + str(article_hour) + ":" + str(article_min)\
                                                               + ":00', '%Y-%m-%d %H:%i:%s')" \
                                                               + ")"
                                    self.cur.execute(sql_insert_table_input)
                                    self.conn.commit()
                                '''
                                for N in range(1, self.input_Verb_table_counter + 1):
                                    sql_insert_table_input = "insert into input_Verb" + str(N) + " (upload_date) values " \
                                                               "(" + "str_to_date('" + str(article_year) + "-" \
                                                               + str(article_month) + "-" + str(article_day) + " " \
                                                               + str(article_hour) + ":" + str(article_min)\
                                                               + ":00', '%Y-%m-%d %H:%i:%s')" \
                                                               + ")"
                                    self.cur.execute(sql_insert_table_input)
                                    self.conn.commit()
                                '''
                            for N in range(1, self.input_Noun_table_counter + 1):
                                for word, count in article_input_Noun_list:
                                    try:
                                        sql_update_table_input = "update input_Noun" + str(N) + " " \
                                                                   "set " + word + " = " + word + " + " + str(count) + " " \
                                                                   "where upload_date = " + "str_to_date('" + str(current_input_datetime) \
                                                                   + "', '%Y-%m-%d %H:%i:%s')"
                                        self.cur.execute(sql_update_table_input)
                                        self.conn.commit()
                                    except:
                                        continue
                            '''
                            for N in range(1, self.input_Verb_table_counter + 1):
                                for word, count in article_input_Verb_list:
                                    try:
                                        sql_update_table_input = "update input_Verb" + str(N) + " " \
                                                                   "set " + word + " = " + word + " + " + str(count) + " " \
                                                                   "where upload_date = " + "str_to_date('" + str(current_input_datetime) \
                                                                   + "', '%Y-%m-%d %H:%i:%s')"
                                        self.cur.execute(sql_update_table_input)
                                        self.conn.commit()
                                    except:
                                        continue
                            '''
                            refined_title = None
                            refined_body = None
                current_date = current_date + datetime.timedelta(days = 1)

            print("****************************** insert table input complete ******************************")

        # input 테이블을 출력하는 메소드
        def Select_Table_Input(self):
            print("****************************** select table input execute ******************************")
            for N in range(1, self.input_Noun_table_counter + 1):
                print("select table input_Noun" + str(N) )
                sql_select_table_input = "select * from input_Noun" + str(N) + " " \
                                           "order by upload_date desc"
                self.cur.execute(sql_select_table_input)
                input_list = self.cur.fetchall()
                for input in input_list:
                    print(input)
            '''
            for N in range(1, self.input_Verb_table_counter + 1):
                print("select table input_Verb :" + str(N) )
                sql_select_table_input = "select * from input_Verb" + str(N) + " " \
                                           "order by upload_date desc"
                self.cur.execute(sql_select_table_input)
                input_list = self.cur.fetchall()
                for input in input_list:
                    print(input)
            '''
            print("****************************** select table input complete ******************************")

        def Clustering_Keyword(self):
            print("****************************** clustering keyword execute ******************************")
            sql_select_table_input = "select upload_date from input_Noun1 order by upload_date desc"
            self.cur.execute(sql_select_table_input)
            datetime_list = self.cur.fetchall()
            cluster_culomn = []
            for datetime in datetime_list:
                culomn = str(datetime)
                cluster_culomn.append(culomn)
            df = pandas.DataFrame(columns = cluster_culomn)
            #print('df =', df)
            #print('11111 Crawler.input_Noun_list =', self.input_Noun_list)
            for word in self.input_Noun_list:
                record = []
                for N in range(1, self.input_Noun_table_counter + 1):
                    try:
                        sql_select_table_input = "select " + word + " from input_Noun" + str(N) + " " \
                                                 "order by upload_date desc"
                        self.cur.execute(sql_select_table_input)
                        count_list = self.cur.fetchall()
                    except:
                        continue
                    #print('22222 count_list =', count_list)
                    for count in count_list:
                        record.append(count[0])
                #print(record)
                df.loc[word] = record
                record.clear()
            data_points = df.values
            #print(data_points)
            kmeans = KMeans(n_clusters = self.cluster_set).fit(data_points) # 클러스터 input 집단 갯수
            print(kmeans.labels_)
            # print(type(kmeans.labels_))
            df['cluster_id'] = kmeans.labels_
            n = 0
            for word in self.input_Noun_list:
                self.input_cluster_dic[word] = kmeans.labels_[n] + 1
                n += 1
            for word in self.input_Noun_list:
                cluster_id = self.input_cluster_dic[word]
                #print("cluster_id =", cluster_id)
                sql_update_keyword_Noun_cluster_id = "update keyword_Noun " \
                                                     "set cluster_id = " + str(cluster_id) + " " \
                                                     "where word = '" + word + "'"
                self.cur.execute(sql_update_keyword_Noun_cluster_id)
                self.conn.commit()
            print("****************************** clustering keyword complete ******************************")

        def Create_Table_Cluster(self):
            print("***************************** create table cluster execute *****************************")
            if self.cluster_table_counter == 0 :
                self.cluster_table_counter += 1
                sql_create_table_cluster = "create table cluster_Noun" + str(self.cluster_table_counter) + " (" \
                                           "upload_date datetime" \
                                           ")"
                self.cur.execute(sql_create_table_cluster)
                print("create table cluster_Noun", self.cluster_table_counter)
            for cluster_id in range(1, self.cluster_set + 1):
                try:
                    sql_alter_table_cluster = "alter table cluster_Noun" + str(self.cluster_table_counter) + " " \
                                              "add cluster" + str(cluster_id) + " smallint default 0"
                    self.cur.execute(sql_alter_table_cluster)
                except:
                    self.cluster_table_counter += 1
                    sql_create_table_cluster = "create table cluster_Noun" + str(self.cluster_table_counter) + " (" \
                                               "upload_date datetime" \
                                               ")"
                    self.cur.execute(sql_create_table_cluster)

                    print("create table cluster_Noun", self.cluster_table_counter)
                    sql_alter_table_cluster = "alter table cluster_Noun" + str(self.cluster_table_counter) + " " \
                                              "add cluster" + str(cluster_id) + " smallint default 0"
                    self.cur.execute(sql_alter_table_cluster)
                    continue
            print("Tne number of cluster_Noun table =", self.cluster_table_counter)
            print("***************************** create table cluster complete *****************************")

        def Insert_Table_Cluster(self):
            print("***************************** insert table cluster execute *****************************")
            print("학습 데이터로 사용할 기사를 추출할 기간을 정해주세요.")
            today_date_time = datetime.datetime.now()
            today_date = today_date_time.strftime('%Y-%m-%d')
            today_year = today_date[0:4]
            today_month = today_date[5:7]
            today_day = today_date[8:10]
            print('현재 날짜 및 시간:', today_date_time)
            print('원하는 수집 기간 입력')
            print("기사 수집 시작 날짜 설정(숫자만 입력)")
            start_year = 2017#input("시작 년도: ")
            start_month = 11#input("시작 월  : ")
            start_day = 28#input("시작 일  : ")
            print("기사 수집 종료 날짜 설정(숫자만 입력)")
            end_year = 2017#input("종료 년도: ")
            end_month = 12#input("종료 월  : ")
            end_day = 4#input("종료 일  : ")
            if int(start_month) < 10:
                start_month = "0" + str(int(start_month))
            if int(start_day) < 10:
                start_day = "0" + str(int(start_day))
            if int(end_month) < 10:
                end_month = "0" + str(int(end_month))
            if int(end_day) < 10:
                end_day = "0" + str(int(end_day))
            start_date_str = str(start_year) + "-" + str(start_month) + "-" + str(start_day) + " " + "00:00:00"
            end_date_str = str(end_year) + "-" + str(end_month) + "-" + str(end_day) + " " + "00:00:00"
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            current_date = start_date
            while current_date <= end_date :
                if current_date.weekday() > 4: # 주식시장은 평일에만 개장하기 때문에 주일, 주말의 기사는 제외함
                    current_date = current_date + datetime.timedelta(days=1)
                    continue
                current_date_str = str(current_date)
                current_year = current_date_str[0:4]
                current_month = current_date_str[5:7]
                current_day = current_date_str[8:10]
                market_start = datetime.time(9, 0, 0)
                market_end = datetime.time(15, 30, 0)
                extend_market_end = datetime.time(15, 35, 0)
                former_input_datetime = datetime.datetime.strptime("9999-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
                page = self.start_page
                while True :
                    '''
                    link_breaking_news_home = "http://news.naver.com/main/list.nhn?mode=LSD&amp;mid=sec&amp;sid1=001&" \
                                              "date=20171026&page=1" # 네이버 뉴스 속보 홈 주소
                    위의 네이버 뉴스 속보 홈 주소에서 data와 page만을 변경하여 각 날짜의 각 페이지에 접속할 수 있음
                    따라서 위의 날짜를 조정하면서 크롤링하여 과거의 데이터를 얻을 수 있음
                    '''
                    page += 1  # 네이버 뉴스 속보 홈에서 원하는 페이지
                    if page > self.end_page : break # 노트북에서는 이 이상으로 데이터를 수집하면 퍼져버려서 임시로 페이지 제한을 둠
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
                    link_sample_article = link_test_article.attrs['href']  # 개별 기사의 링크
                    html_sample_article = urlopen(link_sample_article)
                    try:
                        bsObj_one_article = BeautifulSoup(html_one_article.read(), "html.parser")
                    except:
                        continue
                    # 기사 내용에 따라(시사, 연예 등) html의 양식이 달라져 기사 제목 및 내용을 가져오지 못하는 경우가 있어서 조건문을 통해 반복적인 작업을 실행해야함
                    # 날짜 및 시간 정보를 먼저 수집해서 코드 운용시간 단축
                    date_sample_article = bsObj_sample_article.findAll("span", {"class": "t11"})  # 기사 날짜 가져오기(시사)
                    if str(date_sample_article) == "[]":
                        date_sample_article = bsObj_sample_article.findAll("", {"class": "author"})  # 기사 날짜 다시 가져오기(연예)
                    if str(date_sample_article) == "[]":
                        date_sample_article = bsObj_sample_article.find("div", {"class": "info"})  # 기사 날짜 다시 가져오기(스포츠)
                    if str(date_sample_article) != "[]":
                        str_date = str(date_sample_article)
                        # print(str_date)
                        refined_date = re.sub('[a-zA-Z]', '', str_date)
                        refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_date)
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
                            pass
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
                        try:
                            if article_time > extend_market_end:
                                print(refined_date, "<---- skip page")
                                continue
                            elif article_time < market_start:
                                break
                            else:
                                print(refined_date, "<---- 접근 페이지 첫번째 기사 날짜 및 시간")
                        except:
                            pass
                    else:
                        print("날짜 및 시간 못받음")
                        pass
                    for link_breaking_news_article in bsObj_breaking_news_home.findAll("a", {"class": "nclicks(fls.list)"}):
                        if 'href' in link_breaking_news_article.attrs:  # 해당 페이지 안에 있는 모든 속보 기사 링크를 첫 번째부터 마지막까지 반복적으로 출력함
                            link_one_article = link_breaking_news_article.attrs['href'] # 개별 기사의 링크
                            article_oid = link_one_article[-18:-15]
                            article_aid = link_one_article[-10:]
                            html_one_article = urlopen(link_one_article)
                            try:
                                bsObj_one_article = BeautifulSoup(html_one_article.read(), "html.parser")
                            except:
                                continue
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
                                refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_date)
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
                                    continue
                                if not (article_time >= market_start and article_time <= market_end):
                                    print(refined_date, "<---- out of market time")
                                    continue
                                else:
                                    print(refined_date, "<---- 접근 기사 날짜 및 시간")
                            else:
                                print("날짜 및 시간 못받음")
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
                            article_cluster_Noun_dic = {}
                            #article_clusert_Verb_dic = {}
                            content = refined_title + refined_body
                            if content == None:
                                pass
                            else:
                                article_word_list = twitter.pos(content)
                                for word in article_word_list:
                                    if len(word[0]) <= 1:
                                        continue
                                    if word[0] in self.Noun_filter:
                                        continue
                                    if word[0] in self.Verb_filter:
                                        continue
                                    if (word[1] == "Noun"):
                                        try:
                                            cluster = self.input_cluster_dic[word[0]]
                                        except:
                                            continue
                                        if not (cluster in article_cluster_Noun_dic):
                                            article_cluster_Noun_dic[cluster] = 0
                                        article_cluster_Noun_dic[cluster] += 1
                                    '''
                                    if (word[1] == "Verb"):
                                        if not (word[0] in article_clusert_Verb_dic):
                                            article_clusert_Verb_dic[word[0]] = 0
                                        article_clusert_Verb_dic[word[0]] += 1
                                    '''
                            article_cluster_Noun_list = sorted(article_cluster_Noun_dic.items(), key=lambda x: x[1], reverse=True)
                            #article_input_Verb_list = sorted(article_input_Verb_dic.items(), key=lambda x: x[1], reverse=True)
                            current_input_datetime = datetime.datetime.strptime(
                                str(article_year) + "-" + str(article_month) + "-" + str(article_day) + " " \
                                + str(article_hour) + ":" + str(article_min) + ":00", "%Y-%m-%d %H:%M:%S")
                            # print('과거 vs 현재 인풋 시간 : ' + str(former_input_datetime) + ' vs ' + str(current_input_datetime))
                            if former_input_datetime != current_input_datetime:
                                former_input_datetime = current_input_datetime
                                for N in range(1, self.cluster_table_counter + 1):
                                    sql_insert_table_cluster = "insert into cluster_Noun" + str(N) + " (upload_date) values " \
                                                               "(" + "str_to_date('" + str(article_year) + "-" \
                                                               + str(article_month) + "-" + str(article_day) + " " \
                                                               + str(article_hour) + ":" + str(article_min)\
                                                               + ":00', '%Y-%m-%d %H:%i:%s')" \
                                                               + ")"
                                    self.cur.execute(sql_insert_table_cluster)
                                    self.conn.commit()
                                '''
                                for N in range(1, self.input_Verb_table_counter + 1):
                                    sql_insert_table_input = "insert into input_Verb" + str(N) + " (upload_date) values " \
                                                               "(" + "str_to_date('" + str(article_year) + "-" \
                                                               + str(article_month) + "-" + str(article_day) + " " \
                                                               + str(article_hour) + ":" + str(article_min)\
                                                               + ":00', \'%Y-%m-%d %H:%i:%s\')" \
                                                               + ")"
                                    self.cur.execute(sql_insert_table_input)
                                    self.conn.commit()
                                '''
                            for N in range(1, self.cluster_table_counter + 1):
                                for cluster, count in article_cluster_Noun_list:
                                    try:
                                        sql_update_table_cluster = "update cluster_Noun" + str(N) + " " \
                                                                   "set cluster" + str(cluster) + " = cluster" + str(cluster) + " + " + str(count) + " " \
                                                                   "where upload_date = " + "str_to_date('" + str(current_input_datetime) \
                                                                   + "', '%Y-%m-%d %H:%i:%s')"
                                        self.cur.execute(sql_update_table_cluster)
                                        self.conn.commit()
                                    except:
                                        continue
                            '''
                            for N in range(1, Crawler.input_Verb_table_counter + 1):
                                for cluster, count in article_cluster_Verb_list:
                                    try:
                                        sql_update_table_cluster = "update input_Verb" + str(N) + " " \
                                                                   "set cluster" + cluster + " = cluster" + cluster + " + " + str(count) + " " \
                                                                   "where upload_date = " + "str_to_date('" + str(current_input_datetime) \
                                                                   + "', '%Y-%m-%d %H:%i:%s')"
                                        Crawler.cur.execute(sql_update_table_cluster)
                                        self.conn.commit()
                                    except cx_Oracle.DatabaseError as e:
                                        continue
                            '''
                            refined_title = None
                            refined_body = None
                current_date = current_date + datetime.timedelta(days = 1)

            print("***************************** insert table cluster complete *****************************")

        def Select_Table_Cluster(self):
            print("***************************** select table cluster execute *****************************")
            for N in range(1, self.cluster_table_counter + 1):
                print("select table cluster_Noun :" + str(N) )
                sql_select_table_cluster = "select * from cluster_Noun" + str(N) + " " \
                                           "order by upload_date desc"
                self.cur.execute(sql_select_table_cluster)
                input_list = self.cur.fetchall()
                for input in input_list:
                    print(input)
            '''
            for N in range(1, self.input_Verb_table_counter + 1):
                print("select table input_Verb :" + str(N) )
                sql_select_table_input = "select * from input_Verb" + str(N) + " " \
                                           "order by upload_date desc"
                self.cur.execute(sql_select_table_input)
                input_list = self.cur.fetchall()
                for input in input_list:
                    print(input)
            '''
            print("***************************** select table cluster complete *****************************")

        # input 테이블을 csv 파일로 복사하는 메소드
        def Write_CSV_Input(self):
            print("******************************** write csv input execute ********************************")
            for N in range(1, self.input_Noun_table_counter + 1):
                csv_file = open('input_Noun' + str(N) + '.csv', 'w', encoding='UTF-8')
                csv_writer = csv.writer(csv_file, delimiter=',')
                csv_attrs = ['upload_date'] + self.input_Noun_list[(N-1)*999 : N*999][0] # DB 최대 컬럼 수 반영
                csv_writer.writerow(csv_attrs)
                sql_select_table_input_N = "select * from input_Noun" + str(N) + " " \
                                           "order by upload_date desc"
                self.cur.execute(sql_select_table_input_N)
                article_input_list = self.cur.fetchall()
                for article_input in article_input_list:
                    csv_writer.writerow(article_input)
                print("write csv input_Noun " + str(N))
                csv_file.close()
            print("******************************* write csv input complete *******************************")

        # 실시간으로 기사를 크롤링해서 input 데이터를 얻는 메소드
        def Crawl_Realtime_News(self):
            print("****************************** crawl realtime news execute ******************************")
            realtime_input_Noun = []
            #realtime_input_Verb = []
            for column in range(1, Crawler.cluster_set + 1):
                realtime_input_Noun.append(0)
            #print('realtime_input_Noun :', realtime_input_Noun) # 체크포인트
            present_datetime = datetime.datetime.now()
            #present_datetime = datetime.datetime.strptime("2017-12-01 14:43:00","%Y-%m-%d %H:%M:%S")  # 테스트를 위해 시간을 임의로 지정
            present_datetime = present_datetime - datetime.timedelta(minutes=1)
            present_datetime = present_datetime.replace(second = 0, microsecond = 0)
            print('크롤링 기사 시간 : ', present_datetime) # 체크포인트
            present_datetime_str = present_datetime.strftime('%Y-%m-%d')
            present_year = present_datetime_str[0:4]
            present_month = present_datetime_str[5:7]
            present_day = present_datetime_str[8:10]
            page = 0
            market_start = datetime.time(9, 0, 0)
            market_end = datetime.time(15, 30, 0)
            extend_market_end = datetime.time(15, 35, 0)
            link_breaking_news_home = "http://news.naver.com/main/list.nhn?mode=LSD&sid1=101&mid=sec&listType=title&" \
                                      "date=" + present_year + present_month + present_day + "&page=" + str(page)
            #print(link_breaking_news_home) # 체크포인트
            try:
                html_breaking_news_home = urlopen(link_breaking_news_home)
            except HTTPError as e:
                print(e)
                print("\n\n\n*****오류발생 : 네이버 속보 홈페이지 link 가져오기*****\n\n\n")
            bsObj_breaking_news_home = BeautifulSoup(html_breaking_news_home.read(), "html.parser")
            for link_breaking_news_article in bsObj_breaking_news_home.findAll("a", {"class": "nclicks(fls.list)"}):
                if 'href' in link_breaking_news_article.attrs:  # 해당 페이지 안에 있는 모든 속보 기사 링크를 첫 번째부터 마지막까지 반복적으로 출력함
                    link_one_article = link_breaking_news_article.attrs['href']  # 개별 기사의 링크
                    html_one_article = urlopen(link_one_article)
                    try:
                        bsObj_one_article = BeautifulSoup(html_one_article.read(), "html.parser")
                    except:
                        continue
                    # 기사 내용에 따라(시사, 연예 등) html의 양식이 달라져 기사 제목 및 내용을 가져오지 못하는 경우가 있어서 조건문을 통해 반복적인 작업을 실행해야함
                    # 날짜 및 시간 정보를 먼저 수집해서 코드 운용시간 단축
                    date_one_article = bsObj_one_article.findAll("span", {"class": "t11"})  # 기사 날짜 가져오기(시사)
                    if str(date_one_article) == "[]":
                        date_one_article = bsObj_one_article.findAll("", {"class": "author"})  # 기사 날짜 다시 가져오기(연예)
                    if str(date_one_article) == "[]":
                        date_one_article = bsObj_one_article.find("div", {"class": "info"})  # 기사 날짜 다시 가져오기(스포츠)
                    if str(date_one_article) != "[]":
                        str_date = str(date_one_article)
                        # print(str_date)
                        refined_date = re.sub('[a-zA-Z]', '', str_date)
                        refined_date = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', refined_date)
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
                            continue
                        if not (article_time >= market_start and article_time <= market_end):
                            print(refined_date, "<---- out of market time")
                            continue
                        else:
                            #print(refined_date, "<---- 접근 기사 날짜 및 시간")
                            pass
                    else:
                        print("날짜 및 시간 못받음")
                        continue
                    current_article_datetime = datetime.datetime.strptime(
                        str(article_year) + "-" + str(article_month) + "-" + str(article_day) + " " \
                        + str(article_hour) + ":" + str(article_min) + ":00", "%Y-%m-%d %H:%M:%S")
                    if current_article_datetime < present_datetime:  # 무한루프를 멈추는 부분
                        print('종료시킨 기사 시간 : ', current_article_datetime)  # 체크포인트
                        #print(current_article_datetime < present_datetime)  # 체크포인트
                        break
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
                    article_cluster_Noun_dic = {}
                    # article_cluster_Verb_dic = {}
                    content = refined_title + refined_body
                    if content == None:
                        pass
                    else:
                        article_word_list = twitter.pos(content)
                        for word in article_word_list:
                            if len(word[0]) <= 1:
                                continue
                            if word[0] in self.Noun_filter:
                                continue
                            if word[0] in self.Verb_filter:
                                continue
                            if (word[1] == "Noun"):
                                try:
                                    cluster = self.input_cluster_dic[word[0]]
                                except:
                                    continue
                                if not (cluster in article_cluster_Noun_dic):
                                    article_cluster_Noun_dic[cluster] = 0
                                article_cluster_Noun_dic[cluster] += 1
                            '''
                            if (word[1] == "Verb"):
                                if not (word[0] in article_clusert_Verb_dic):
                                    article_clusert_Verb_dic[word[0]] = 0
                                article_clusert_Verb_dic[word[0]] += 1
                            '''
                    article_cluster_Noun_list = sorted(article_cluster_Noun_dic.items(), key=lambda x: x[1],reverse=True)
                    # article_input_Verb_list = sorted(article_input_Verb_dic.items(), key=lambda x: x[1], reverse=True)
                    #print(article_cluster_Noun_list) # 체크포인트
                    for cluster, count in article_cluster_Noun_list:
                        realtime_input_Noun[cluster-1] += count
                    refined_title = None
                    refined_body = None
            #print('realtime_input_Noun =', realtime_input_Noun)
            print("***************************** crawl realtime news complete *****************************")
            return realtime_input_Noun

        def Regular_Crawling(self):
            timer = threading.Timer(60, self.Regular_Crawling())
            if datetime.datetime.now() > datetime.datetime.strptime("2017-12-04 20:09:00", '%Y-%m-%d %H:%M:%S'):
                print('실시간 크롤링 종료')
                timer.cancel()
            print('실시간 크롤링 시간 =', datetime.datetime.now())
            result = self.Crawl_Realtime_News()
            print('실시간 input return =', result)
            timer.start()




# 학습을 위한 cluster table을 만드는 함수 나열
crawler = Crawler()
crawler.Connect_To_Database()

crawler.Create_Table_Keyword()
crawler.Insert_Table_Keyword()

crawler.Create_Table_Input()
crawler.Insert_Table_Input()

crawler.Clustering_Keyword()
crawler.Create_Table_Cluster()
crawler.Insert_Table_Cluster()
crawler.Store_Crawler()

crawler.Close_To_Database()
