from jinja2 import Template

per = {'name': 'Федор', 'age': '35'}
tm = Template("имя =  {{ p['name'] }}, возраст = {{ p['age'] }}")
msg = tm.render(p=per)
print(msg)
