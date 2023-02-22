from mailmerge import MailMerge #pip install docx-mailmerge

document = MailMerge('template.docx') 

print(document.get_merge_fields())

merge_files = { 'Title':'My Title 3', 'Sub1':'My First Sub Heading', 'Sub1Text':'My first paragraph\nNew line?', 'Sub2':'My Second Sub Heading', 'Sub2Text':'My final closing paragraph.'}

document.merge(**merge_files)

document.write('output.docx')