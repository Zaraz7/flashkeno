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
                ('clearnet', 'https://ockolus.neocities.org/'),
                ('gemini', 'gemini://ockolus.space/')
            ]
        },
        {
            'name': 'Пример форума',
            'button': 'forum_button.gif',
            'about': 'Интересный форум для общения',
            'type': 'форумы',
            'urls': [
                ('clearnet', 'https://example-forum.com/'),
                ('i2p', 'http://forum.i2p/')
            ]
        },
        {
            'name': 'Социальная сеть',
            'button': 'social_button.gif',
            'about': 'Новая социальная сеть для разработчиков',
            'type': 'соцсети',
            'urls': [
                ('clearnet', 'https://social.example.com/'),
                ('zeronet', 'http://127.0.0.1:43110/social.bit/')
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