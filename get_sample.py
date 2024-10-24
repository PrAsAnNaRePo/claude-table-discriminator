import json

data = json.load(open('data_updates.json', 'r'))

print(len(data['image']))

selected_rows = []

for i in range(len(data['image'])):
    if data['time'][i].startswith('2024-10-21') and data['file_name'][i].startswith('HF24') and data['page_num'][i] == '35':
        selected_rows.append(
            {
                'page_num': data['page_num'][i],
                'image': data['image'][i],
                'response': data['response'][i],
            }
        )

print(len(selected_rows))

with open('sample.json', 'w') as f:
    json.dump(selected_rows, f)
