#!/usr/bin/env python3
import argparse
from lib.database import SiteDatabase
import config
from pathlib import Path

db = SiteDatabase(Path(__file__).parent / 'db' / 'sites.db')

def cmd_list(args):
    sites = db.get_all_sites()
    if not sites:
        print('No sites')
        return
    for s in sites:
        urls = ', '.join(f"{u['type']}={u['url']}" for u in s['urls'])
        print(f"{s['id']:3d} | {s.get('type') or '-':15} | {s['name']} | {s['button']} | {urls}")

def cmd_add(args):
    urls = []
    for u in args.urls or []:
        if '=' not in u:
            print('Bad url format, expected type=url')
            return
        t, url = u.split('=',1)
        urls.append((t, url))
    sid = db.add_site(args.name, args.button or '', args.about or '', args.type, urls)
    print('Added', sid)

def cmd_edit(args):
    ok = db.update_site(args.id, name=args.name, button=args.button, about=args.about, type_name=args.type)
    if not ok:
        print('Site not found')
        return
    if args.replace_urls is not None:
        urls = []
        for u in args.replace_urls:
            if '=' not in u:
                print('Bad url format')
                return
            t, url = u.split('=',1)
            urls.append((t, url))
        db.replace_urls(args.id, urls)
    print('Updated', args.id)

def cmd_delete(args):
    if db.delete_site(args.id):
        print('Deleted', args.id)
    else:
        print('Site not found')

def cmd_move(args):
    if db.move_site(args.id, args.direction):
        print('Moved', args.id, args.direction)
    else:
        print('Cannot move')

def cmd_find(args):
    res = db.find_sites(args.query)
    for s in res:
        print(f"{s['id']:3d} | {s['type'] or '-':15} | {s['name']}")

def cmd_suggestions_list(args):
    """Показать список заявок"""
    status = args.status if hasattr(args, 'status') else None
    suggestions = db.get_suggestions(status)
    
    if not suggestions:
        print('No suggestions found')
        return
    
    print(f"{'ID':4} | {'Статус':10} | {'Имя':20} | {'Тип':15} | {'URL':30} | {'Дата':20}")
    print('-' * 105)
    for s in suggestions:
        print(f"{s['id']:4d} | {s['status']:10} | {s['name'][:20]:20} | {s['type'] or '-':15} | {s['url'][:30]:30} | {s['submitted_at'][:19]:20}")

def cmd_suggestions_show(args):
    """Показать подробную информацию о заявке"""
    suggestion = db.get_suggestion(args.id)
    if not suggestion:
        print(f'Suggestion {args.id} not found')
        return
    
    print(f"ID: {suggestion['id']}")
    print(f"Статус: {suggestion['status']}")
    print(f"Имя: {suggestion['name']}")
    print(f"Email: {suggestion['email'] or '-'}")
    print(f"URL: {suggestion['url']}")
    print(f"Кнопка: {suggestion['button'] or '-'}")
    print(f"Описание: {suggestion['about']}")
    print(f"Тип: {suggestion['type'] or '-'}")
    print(f"IP клиента: {suggestion['client_ip']}")
    print(f"User-Agent: {suggestion['client_agent']}")
    print(f"Дата подачи: {suggestion['submitted_at']}")

def cmd_suggestions_approve(args):
    """Одобрить заявку и создать сайт"""
    site_id = db.approve_suggestion(args.id)
    if site_id:
        print(f'Suggestion {args.id} approved, site created with ID: {site_id}')
    else:
        print(f'Cannot approve suggestion {args.id}')

def cmd_suggestions_reject(args):
    """Отклонить заявку (отправить в корзину)"""
    if db.update_suggestion_status(args.id, 'rejected'):
        print(f'Suggestion {args.id} rejected')
    else:
        print(f'Cannot reject suggestion {args.id}')

def cmd_suggestions_delete(args):
    """Удалить заявку"""
    if db.delete_suggestion(args.id):
        print(f'Suggestion {args.id} deleted')
    else:
        print(f'Cannot delete suggestion {args.id}')

def main():
    p = argparse.ArgumentParser(prog='sitectl')
    sub = p.add_subparsers(dest='cmd')
    a = sub.add_parser('list'); a.set_defaults(func=cmd_list)

    a = sub.add_parser('add'); a.add_argument('--name', required=True); a.add_argument('--button'); a.add_argument('--about'); a.add_argument('--type', required=True); a.add_argument('--urls', nargs='*'); a.set_defaults(func=cmd_add)

    a = sub.add_parser('edit'); a.add_argument('id', type=int); a.add_argument('--name'); a.add_argument('--button'); a.add_argument('--about'); a.add_argument('--type'); a.add_argument('--replace-urls', nargs='*'); a.set_defaults(func=cmd_edit)

    a = sub.add_parser('delete'); a.add_argument('id', type=int); a.set_defaults(func=cmd_delete)

    a = sub.add_parser('move'); a.add_argument('id', type=int); a.add_argument('direction', choices=['up','down']); a.set_defaults(func=cmd_move)

    a = sub.add_parser('find'); a.add_argument('query'); a.set_defaults(func=cmd_find)

    a = sub.add_parser('suggestions-list', help='List all suggestions')
    a.add_argument('--status', choices=['pending', 'approved', 'rejected'], help='Filter by status')
    a.set_defaults(func=cmd_suggestions_list)
    
    a = sub.add_parser('suggestions-show', help='Show suggestion details')
    a.add_argument('id', type=int, help='Suggestion ID')
    a.set_defaults(func=cmd_suggestions_show)
    
    a = sub.add_parser('suggestions-approve', help='Approve suggestion and create site')
    a.add_argument('id', type=int, help='Suggestion ID')
    a.set_defaults(func=cmd_suggestions_approve)
    
    a = sub.add_parser('suggestions-reject', help='Reject suggestion (move to trash)')
    a.add_argument('id', type=int, help='Suggestion ID')
    a.set_defaults(func=cmd_suggestions_reject)
    
    a = sub.add_parser('suggestions-delete', help='Delete suggestion')
    a.add_argument('id', type=int, help='Suggestion ID')
    a.set_defaults(func=cmd_suggestions_delete)



    args = p.parse_args()
    if not hasattr(args, 'func'):
        p.print_help()
        return
    args.func(args)

if __name__ == '__main__':
    main()