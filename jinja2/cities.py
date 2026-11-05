from jinja2 import Template

per = [{'name': 'Федор', 'age': '35'},
       {'name': 'Федор2', 'age': '35'},
       {'name': 'Федор3', 'age': '35'},
       {'name': 'Федор4', 'age': '35'}]

div = '''<div name="per">
{% for p in per %}
    <div>{{ p['name'] }}, {{ p['age'] }}</div>
{% endfor %}
</div>'''

tm = Template(div)
msg = tm.render(per=per)
print(msg)
