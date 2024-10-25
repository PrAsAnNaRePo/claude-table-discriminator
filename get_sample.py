import json

data = json.load(open('data.json', 'r'))

print(len(data['image']))

selected_rows = []

FILE_STARTS = 'HF29'
DATE = '2024-10-23'
PG_NO = '11'

c = 0
for i in range(len(data['image'])):
    if data['time'][i].startswith(DATE) and data['file_name'][i].startswith(FILE_STARTS) and data['page_num'][i] == PG_NO:
        c += 1
        print(f"got {c}")
        with open(f'{FILE_STARTS}-table-{c}-pg-{PG_NO}-base64.txt', 'w') as img_file:
            img_file.write(data['image'][i])
        
        with open(f'{FILE_STARTS}-table-{c}-pg-{PG_NO}-response.txt', 'w', encoding="utf-8") as response_file:
            response_file.write(str(data['response'][i]))
        
        
        # selected_rows.append(
        #     {
        #         'page_num': data['page_num'][i],
        #         'image': data['image'][i],
        #         'response': data['response'][i],
        #     }
        # )