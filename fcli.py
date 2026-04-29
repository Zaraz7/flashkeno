#!/usr/bin/env python3
import argparse
from app.database import SiteDatabase

db = SiteDatabase()

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

def main():
    p = argparse.ArgumentParser(prog='sitectl')
    sub = p.add_subparsers(dest='cmd')
    a = sub.add_parser('list'); a.set_defaults(func=cmd_list)

    a = sub.add_parser('add'); a.add_argument('--name', required=True); a.add_argument('--button'); a.add_argument('--about'); a.add_argument('--type', required=True); a.add_argument('--urls', nargs='*'); a.set_defaults(func=cmd_add)

    a = sub.add_parser('edit'); a.add_argument('id', type=int); a.add_argument('--name'); a.add_argument('--button'); a.add_argument('--about'); a.add_argument('--type'); a.add_argument('--replace-urls', nargs='*'); a.set_defaults(func=cmd_edit)

    a = sub.add_parser('delete'); a.add_argument('id', type=int); a.set_defaults(func=cmd_delete)

    a = sub.add_parser('move'); a.add_argument('id', type=int); a.add_argument('direction', choices=['up','down']); a.set_defaults(func=cmd_move)

    a = sub.add_parser('find'); a.add_argument('query'); a.set_defaults(func=cmd_find)

    args = p.parse_args()
    if not hasattr(args, 'func'):
        p.print_help()
        return
    args.func(args)

if __name__ == '__main__':
    main()