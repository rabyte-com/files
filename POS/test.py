import os
import stat
from datetime import datetime
from hdbcli import dbapi

run_date = datetime.now().date().strftime("%d-%m-%Y")
date1 = datetime.now().date().strftime("%y%m%d")
now = datetime.now().strftime("%H%M")
run_time = datetime.now().strftime("%H_%M")
seq_no = 12534
date2 = datetime.now().date().strftime("%Y%m%d")

# create a connection with SAP LLP server for fetching data
connection = dbapi.connect(
    address="103.25.172.160",
    port=30015,
    database="RABYTE_PTE_LIVE",
    user="SYSTEM",
    password="Data1234",
)

query = f""" 
    SELECT "LineNum" as "Item No",T1."U_UTL_BPREF" as "PO Number" , 'Invoice' as "Type" , T0."DocNum" as "Invoice Document No",
T0."CardCode" as "Customer Code",T0."CardName" as "Customer Name",T0."Address" as "Address 1",
 T0."Address2" as "Address 2", T3."StateB" as "State",  T3."CountyB" as "Country",
T3."ZipCodeB" as "Zip Code",T3."CityB" as "City",T1."LineNum" as "Lines Item No",T1."ItemCode" as "Item Code",
T1."Dscription" as "Item Name/Description",T1."unitMsr" as "UOM",
T1."Quantity" as "Qty",T1."Price" as "Sale Unit Price",T0."DocCur" as "Currency",'' as "Disty Book Cost",
'' as "Adjust Cost",T1."U_UTL_BPREF" as "Customer PO",
T4."U_RENESCMNO" as "SCM Code",T5."U_COO" as "COO-Company of Origin",T4."U_RENE_ABU" as "ABU/IIBU",
'' as "End Customer Code",
T0."ShipToCode" as "End Customer Name",
T0."Address2" as "End Address 2" ,

T3."StateS" as "End State",
T3."CountyS" as "End Country",  
T3."ZipCodeS" as "End Zip Code",
T3."CityS" as "End City",
'' as "SCM No of End Customer",
T1."U_SAMPLETYPE" as "Sample Type",
T1."U_FOC" as "FOC Sample",
'' as "S&D No",
'' as "S&D Qty",'' as "S&D Balance Qty",
'' as "S&D Price",
'' as "S&D Date From",
'' as "S&D Date To",
'' as "S&D Customer Code",
'' as "S&D Customer Name",
'' as "S&D Customer Name",
T4."U_OsramCustNo" as  "Osram End CustNo",
T0."U_Project" as "Project Name",
'' as "Project No",
T7."Name" "Make",
T6."Name" as "Make+Div"

FROM "RABYTE_PTE_LIVE".OINV T0

INNER JOIN "RABYTE_PTE_LIVE".INV1 T1 ON T1."DocEntry"=T0."DocEntry"
LEFT JOIN "RABYTE_PTE_LIVE".INV12 T3 ON T3."DocEntry"=T1."DocEntry"
LEFT JOIN "RABYTE_PTE_LIVE".OITM T2 ON T2."ItemCode"=T1."ItemCode"
LEFT JOIN "RABYTE_PTE_LIVE".OCRD T4 ON T4."CardCode"=T0."CardCode"
LEFT JOIN "RABYTE_PTE_LIVE".OITM T5 ON T5."ItemCode"=T1."ItemCode"
LEFT JOIN "RABYTE_PTE_LIVE"."@MAKE_FULL_2" T6 ON T6."Code"= T5."U_M_F_2"
LEFT JOIN "RABYTE_PTE_LIVE"."@MAKE_FULL_1" T7 ON T7."Code"= T5."U_MF_1"
WHERE T0."DocType"='I'

"""

cursor = connection.cursor()
cursor.execute(query)
pos = cursor.fetchall()

reqfolder = f"POS_report"
file_name = f"{reqfolder}/EDI_POS_IDTEDIUS_{run_date}_{run_time}.txt"

if not os.path.exists(reqfolder):
    os.makedirs(reqfolder)
    os.chmod(reqfolder, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


with open(file_name, "w") as file:
    line_count = 7
    file.write(
        f"ISA*00*          *00*          *ZZ*RABYTEEDI      *ZZ*<SOLD_TO_ID>         *{date1}*{now}*U*00401*00000{seq_no}*0*T*>]\n"
    )
    file.write(f"GS*PT*RABYTEEDI*<SOLD_TO_ID>*{date2}*{now}*{seq_no}*X*004010]\n")
    file.write(f"ST*867*{seq_no}]\n")
    file.write(f"BPT*00*{seq_no}*{date2}*02]\n")
    file.write(f"CUR*DS*USD]\n")
    file.write(f"N1*BY*RENE*91*114571]\n")
    for invoice_no, line_details in pos.items():
        flag = 0
        index = 1
        qty_sum = 0
        for po_details in line_details:
            file.write(f"PTD*SD]\n")  # replace SD wiht RP if the POS is NEGATIVES
            file.write(
                f"N1*ST*<SELL_THROUGH_CUST_NAME>*92*CA00005335]\n"
            )  # If the item tagged with Rene-EP then System will add CA no from BP Master else customer name will be printed
            file.write(
                f"N3*<ADDRESS 1>*<ADDRESS 2>]\n"
            )  # Max Length 55 characters per address line.
            file.write(f"N4*<CITY>*<STATE_CODE>*<PIN_CODE>*<COUNTRY_CODE>]\n")

            """ 
                If Sell through Customer will be same as End Customer the same 
                Information of N1, N3, N4 will be populated in end customer segment fields. 
                Otherwise, the information will be populated from the End Customer Master Data.
            """

            file.write(
                f"N1*ST*<END_CUST_NAME>*92*CA00005335]\n"
            )  # If the item tagged with Rene-EP then System will add CA no from BP Master else customer name will be printed
            file.write(
                f"N3*<ADDRESS 1>*<ADDRESS 2>]\n"
            )  # Max Length 55 characters per address line.
            file.write(f"N4*<CITY>*<STATE_CODE>*<PIN_CODE>*<COUNTRY_CODE>]\n")
            file.write(f"QTY*<LINE_NUMBER>*<QTY>*EA]\n")
            file.write(f"LIN*{index}*VP*<PATRT_NUMBER>]\n")
            file.write(f"UIT*EA*<INV_SALE_PRICE>*RS]\n")
            file.write(f"UIT*EA*<DBC_PRICE>*RS]\n")
            file.write(f"UIT*EA*<DC_PRICE>*RS]\n")
            file.write(f"REF*CO*<CUST_PO_NUMBER]\n")
            file.write(f"REF*AU*<S&D_NUMBER>]\n")
            file.write(f"REF*DI*<INVOICE_NUMBER>]\n")
            file.write(f"REF*LI*<LINE_NUMBER>]\n") 
            # if credit_note is negative:
            # file.write(f"REF*CM*CN#**LI>LINE#]\n")
            # flag = 1
            file.write(f"DTM*003*<PO_DATE>]\n")
            index += 1
            if flag == 0:
                line_count += 16
            else: 
                line_count += 17
    file.write(f"CTT*{index-1}*{qty_sum}]\n")
    file.write(f"SE*{line_count}*{seq_no}]\n")
    file.write(f"GE*1*{seq_no}]\n")
    file.write(f"IEA*1*00000{seq_no}]\n")

print("🟢🟢 Done exporting!!")
print ("end")