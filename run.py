import openai, time, json, transformers, re
from mailmerge import MailMerge #pip install docx-mailmerge

MAX_TOKEN_COUNT = 4097
GPT_MODEL = "text-davinci-003"
GPT_TEMP = 0
GPT_FREQ = 0.0
GPT_PRES = 0.0
GBP_TOPP = 1.0
GPT_CALL_OUT_ON = True

# Set up your OpenAI API key
openai.api_key = "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"

def remove_digits_period(string): 
    modified_string = ''
    for i, char in enumerate(string):
        if i < 4 and (char.isdigit() or char == '.'):
            continue
        modified_string += char
    return modified_string.strip()

def remove_chapter(string):
    #pattern = r'^((Chapter)?\s*\d+(\.\d+)*\s*:\s*)*'
    pattern = r'^((Chapter)?\s*\d+(\.\d+)*)\s*:\s*'
    regex = re.compile(pattern)
    text = regex.sub('', string)
    return remove_digits_period(text)

def token_count(prompt):
    global GPT_CALL_OUT_ON
    if not GPT_CALL_OUT_ON: return 0
    tokenizer = transformers.AutoTokenizer.from_pretrained("openai-gpt")
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)+500

def gpt_complete(prompt,token_size):
    global GPT_CALL_OUT_ON
    if GPT_CALL_OUT_ON:
        response = openai.Completion.create(
                                  model=GPT_MODEL,
                                  prompt=prompt,
                                  temperature=GPT_TEMP,
                                  max_tokens=token_size,
                                  top_p=GBP_TOPP,
                                  frequency_penalty=GPT_FREQ,
                                  presence_penalty=GPT_PRES
                            )
        return response.choices[0].text
    else:
        return '[{"chapter":"Introduction","subchapters":[]},{"chapter":"Middle Section","subchapters":["Middle 1","Middle 2","Middle 3"]},{"chapter":"End Section","subchapters":["End 1","End 2"]},{"chapter":"Conclusion","subchapters":[]}]'
    

if __name__ == '__main__':

    '''merge_fields = '{ '
    merge_fields += "Title":"","TableOfContents",'
    merge_fields += "C1":"","C1-S1":"","C1-S2":"","C1-S3":"",'
    merge_fields += '"C2":"","C2-S1":"","C2-S2":"","C2-S3":"",'
    merge_fields += '"C3":"","C3-S1":"","C3-S2":"","C3-S3":"",'
    merge_fields += '"C4":"","C3-S1":"","C3-S2":"","C3-S3":""'
    merge_fields += ' }''' 

    title = input('Give your book a title: ')
    output_file = title.replace(' ','_').replace('/','-') + '.txt'
    subject = input('What is your book about? This book is about...')
    with open(output_file, 'w') as f:
        f.write(title.upper()+'\n\n')
        print(title.upper())
        f.write('Table of contents:\n\n') 
        print('\n\nTable of contents:\n\n')
    prompt = f'Write the table of contents for a book called "{title}" about {subject}. Return the result as a JSON object using the following template: '
    prompt += '{[{"chapter":"","subchapters":[]}]}. Provide only the JSON object as the only response, and do no provide any commentary before or after the JSON object.'
    json_result = gpt_complete(prompt,MAX_TOKEN_COUNT-token_count(prompt))
    print(json_result) 
    time.sleep(1)
    json_obj = json.loads(json_result)
    toc = ''
    with open(output_file, 'a') as f: 
        for i, chapter in enumerate(json_obj,start=1):
            toc_item = '  '+str(i)+': ' +remove_chapter(chapter['chapter']) + '\n'
            toc += toc_item
            f.write(toc)  
            if chapter['subchapters']: 
                for j, item in enumerate(chapter['subchapters'],start=1):
                    toc_item = '     '+str(i)+'.'+str(j)+': '+remove_chapter(item)+'\n'
                    toc += toc_item
                    f.write(toc_item) 
        f.write('\n') 
    
    print(toc)
    # Iterate through the list of book chapters
    
    input_dict = {"Title": title, "TOC": toc}
    input_json = json.dumps(input_dict)    
    merge_json = json.loads(input_json)
    
    for i, chapter in enumerate(json_obj,start=1):
    
        chapter_clean = remove_chapter(chapter['chapter'])
        chapter_numbered_without_linebreak = str(i) + '.0: ' + chapter_clean       
        chapter_numbered_with_linebreak = chapter_numbered_without_linebreak + '\n\n' 
        merge_json[str(i)+'.0'] = chapter_numbered_without_linebreak
        
        with open(output_file, 'a') as f: 
            f.write(chapter_numbered_with_linebreak) 
            print(chapter_numbered_with_linebreak)
            
        if chapter['subchapters']: 
            for j, item in enumerate(chapter['subchapters'],start=1):
                subchapter_clean = remove_chapter(item)
                subchapter_numbered_without_linebreak = str(i)+'.'+str(j)+': '+subchapter_clean 
                subchapter_numbered_with_linebreak = subchapter_numbered_without_linebreak + '\n\n'  
                merge_json[str(i)+'.'+str(j)] = subchapter_numbered_without_linebreak
                
                with open(output_file, 'a') as f: 
                    f.write(subchapter_numbered_with_linebreak)
                    print(subchapter_numbered_with_linebreak )
                    
                prompt = f'Acting as an expert on "{subject}", write the contents of a subchapter titled "{subchapter_clean}" from the chapter "{chapter_clean}" from a book titled "{title}". Do not include the subchapter title in your response, only the body.'
                # Get the completed text from the response
                if GPT_CALL_OUT_ON:
                    res = gpt_complete(prompt,MAX_TOKEN_COUNT-token_count(prompt))+'\n\n'
                else:
                    res = 'Random paragraph for sub chapter...\n\n'
                # Write the completed text to the output file
                with open(output_file, 'a') as f:
                    f.write(res)
                    print(res)
                    merge_json[str(i)+'.'+str(j)+'-BODY'] = res
                # Wait for a moment to avoid hitting API rate limits
                time.sleep(1)
        else:
            prompt = f'Acting as an expert on "{subject}", write the contents of a chapter titled "{chapter_clean}" from a book titled "{title}". Do not include the chapter title in your response, only the body.'
            if GPT_CALL_OUT_ON:
                res = gpt_complete(prompt,MAX_TOKEN_COUNT-token_count(prompt))+'\n\n'
            else:
                res = 'Random paragraph for chapter...\n\n'
            res = remove_chapter(res)+'\n\n'
            with open(output_file, 'a') as f:
                f.write(res)
                print(res)
                merge_json[str(i)+'.0-BODY'] = res

    #print(json.dumps(merge_json, indent=4))
    with open(output_file.replace('txt','json'), 'w') as f:
        f.write(json.dumps(merge_json, indent=4))
    
    document = MailMerge('template.docx')  
    document.merge(**merge_json) 
    document.write(output_file.replace('txt','docx'))
    
    print('Output files: ')
    print('RAW TEXT:' + output_file)
    print('JSON:' + output_file.replace('txt','json'))
    print('DOCX:' + output_file.replace('txt','docx'))