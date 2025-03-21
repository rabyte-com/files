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

# csreate a connection with SAP LLP server for fetching data
connection = dbapi.connect(
    address="103.25.172.160",
    port=30015,
    database="RABYTE_LLP_LIVE01_0808",
    user="SYSTEM",
    password="Data1234",
)

pos = {
    "23456": {
        "qty": 10,
        "price": 100,
        "date": "2021-08-08",
        "invoice_no": "INV-1234",
    },
    "23457": {
        "qty": 10,
        "price": 100,
        "date": "2021-08-08",
        "invoice_no": "INV-1234",
    },
}


reqfolder = f"POS_report"
file_name = f"{reqfolder}/EDI_POS_IDTEDIUS_{run_date}_{run_time}.txt"

if not os.path.exists(reqfolder):
    os.makedirs(reqfolder)
    os.chmod(reqfolder, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


with open(file_name, "w") as file:
    line_count = 7
    file.write(
        f"ISA*00*          *00*          *ZZ*RABYTEEDI      *ZZ*IDTEDIIUS         *{date1}*{now}*U*00401*00000{seq_no}*0*T*>]\n"
    )
    file.write(f"GS*PT*RABYTEEDI*<SOLD_TO_ID>*{date2}*{now}*{seq_no}*X*004010]\n")
    file.write(f"ST*867*{seq_no}]\n")
    file.write(f"BPT*00*{seq_no}*<POS_DATE>*02]\n")
    file.write(f"CUR*DS*USD]\n")
    file.write(f"N1*BY*<DISTY_NAME>*91*<SOLD_TO_ID>]\n")
    file.write(f"PTD*SD]\n")  # replace SD wiht RP if the POS is NEGATIVES
    for invoice_no, line_details in pos.items():
        flag = 0
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
        index = 1
        qty_sum = 0
        for po_details in line_details:
            file.write(f"QTY*<LINE_NUMBER>*<QTY>*EA]\n")
            file.write(f"LIN*{index}*VP*<PATRT_NUMBER>]\n")
            file.write(f"UIT*EA*<INV_SALE_PRICE>*RS]\n")
            file.write(f"UIT*EA*<DBC_PRICE>*RS]\n")
            file.write(f"UIT*EA*<DC_PRICE>*RS]\n")
            file.write(f"REF*CO*<CUST_PO_NUMBER]\n")
            file.write(f"REF*AU*<UNKNOWN_NUMBER>]\n")
            index += 1

        file.write(f"REF*DI*<INVOICE_NUMBER>]\n")
        file.write(f"REF*LI*<LINE_NUMBER>]\n")
        # if credit_note is negative:
        # file.write(f"REF*CM*CN#**LI>LINE#]\n")
        # flag = 1
        file.write(f"DTM*003*<PO_DATE>]\n")

        if flag == 0:
            line_count += 16
        else:
            line_count += 17
    file.write(f"CTT*{index-1}*{qty_sum}]\n")
    file.write(f"SE*{line_count}*{seq_no}]\n")
    file.write(f"GE*1*{seq_no}]\n")
    file.write(f"IEA*1*00000{seq_no}]\n")

print("🟢🟢 Done exporting!!")
