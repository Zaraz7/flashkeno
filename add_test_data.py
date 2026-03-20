from database import SiteDatabase

def add_test_data():
    db = SiteDatabase()
    
    sites_data = [
        {
            'name': 'Ockolus',
            'button': 'Гифка с Gifius.ru (1).gif',
            'about': 'Сайт не имеет конкретной направленности, это просто поток идей и сознания, который бесконечно стремится к конечной идее. Рада всем, постараюсь в дальнейшем на сайт выкладывать туториалы, мысли, и ресурсы для разработчика',
            'type': 'персональные сайты',
            'urls': [
                ('clearnet', 'https://ockolus.neocities.org/')
            ]
        },
        {
            'name': 'Форум народ',
            'button': 'narodf.gif',
            'about': 'Пользоваться форумом имеют право все желающие, в том числе и на тематику, даже не по теме <a href="http://w10.host" target="_blank" title="Web 1.0 hosting">хостинга</a>, в соответствующих разделах. Давайте возродим форумы, как полезное средство обмена информацией и интересного времяпровождения.',
            'type': 'форумы',
            'urls': [
                ('clearnet', 'https://forum.narod.ws/')
            ]
        },
        {
            'name': 'LainLife',
            'button': 'lainlife.gif',
            'about': 'Первый инстанс OpenVK в Yggdrasil. Проект с открытым исходным кодом, воспроизводящий интерфейс и функционал «ВКонтакте» конца 2000‑х годов',
            'type': 'соцсети',
            'urls': [
                ('clearnet', 'https://lainlife.ru/'),
                ('yggdrasil', 'http://[201:ea34:3017:90a7:d05b:5fd7:5c3b:a77f]/'),
                ('yggdrasil', 'http://lainlife.ygg/')
            ]
        }
    ]
    
    for site_data in sites_data:
        site_id = db.add_site(
            name=site_data['name'],
            button=site_data['button'],
            about=site_data['about'],
            type_name=site_data['type'],
            urls=site_data['urls']
        )
        print(f"Добавлен сайт '{site_data['name']}' с ID: {site_id}")
    
    print("\nВсе тестовые данные успешно добавлены!")

if __name__ == "__main__":
    add_test_data()