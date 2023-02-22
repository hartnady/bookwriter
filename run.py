import openai, time, json, transformers

MAX_TOKEN_COUNT = 4097
GPT_MODEL = "text-davinci-003"
GPT_TEMP = 0
GPT_FREQ = 0.0
GPT_PRES = 0.0
GBP_TOPP = 1.0

# Set up your OpenAI API key
openai.api_key = "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"

def token_count(prompt):
    tokenizer = transformers.AutoTokenizer.from_pretrained("openai-gpt")
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)+500

def gpt_complete(prompt,token_size):
	response = openai.Completion.create(
                              model=GPT_MODEL,
                              prompt=prompt,
                              temperature=GPT_TEMP,
                              max_tokens=token_size,
                              top_p=GBP_TOPP,
                              frequency_penalty=GPT_FREQ,
                              presence_penalty=GPT_PRES
                        )
	print(response.choices[0].text)
	return response.choices[0].text  


if __name__ == '__main__':
	title = input('Give your book a title: ')
	output_file = title.replace(' ','_').replace('/','-') + '.txt' 

	with open(output_file, 'w') as f:
	    f.write(title)
	    print(title)
	    f.write('\n\nTable of contents:\n\n') 
	    print('\n\nTable of contents:\n\n')

	subject = input('What is your book about? This book is about...')

	prompt = f'Write the table of contents for a book called "{title}" about {subject}. Return the result as a JSON object using the following template: '
	prompt += '{[{"chapter":"","subchapters":[]}]}. Provide only the JSON object as the only response, and do no provide any commentary before or after the JSON object.'

	json_result = gpt_complete(prompt,MAX_TOKEN_COUNT-token_count(prompt))
	time.sleep(1)

	json_obj = json.loads(json_result)

	with open(output_file, 'a') as f: 
		for i, chapter in enumerate(json_obj,start=1):
			f.write('  '+str(i)+': ' +chapter['chapter'] + '\n') 
			print('  '+str(i)+': ' +chapter['chapter'] + '\n') 
			if chapter['subchapters']: 
				for j, item in enumerate(chapter['subchapters'],start=1):
					f.write('     '+str(i)+'.'+str(j)+': '+item+'\n')
					print('     '+str(i)+'.'+str(j)+': '+item+'\n')
		f.write('\n') 

	# Iterate through the list of book chapters
	for i, chapter in enumerate(json_obj,start=1):

		curr_chapter = chapter['chapter']

		with open(output_file, 'a') as f: 
			f.write(str(i)+': ' +curr_chapter + '\n\n') 
			print(str(i)+': ' +curr_chapter + '\n\n')  

		if chapter['subchapters']: 

			for j, item in enumerate(chapter['subchapters'],start=1):

				with open(output_file, 'a') as f: 
					f.write(str(i)+'.'+str(j)+': '+item+'\n\n')
					print(str(i)+'.'+str(j)+': '+item+'\n\n')

				prompt = f'Acting as an expert on "{subject}", write the contents of a subchapter titled "{item}" from the chapter "{curr_chapter}" from a book titled "{title}"'

			    # Get the completed text from the response
				res = gpt_complete(prompt,MAX_TOKEN_COUNT-token_count(prompt))

			    # Write the completed text to the output file
				with open(output_file, 'a') as f:
					f.write(res+'\n\n')
					print(res+'\n\n')

			    # Wait for a moment to avoid hitting API rate limits
				time.sleep(0.1)

		else:

			prompt = f'Acting as an expert on "{subject}", write the contents of a chapter titled "{curr_chapter}" from a book titled "{title}"'
			res = gpt_complete(prompt,MAX_TOKEN_COUNT-token_count(prompt))

			with open(output_file, 'a') as f:
				f.write(res+'\n\n')
				print(res+'\n\n')
