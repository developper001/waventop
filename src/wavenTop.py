import json
import pathlib
import requests
import os, shutil
from pyquery import PyQuery    
from datetime import datetime
from yattag import Doc, indent

class WavenDbTop:
  config = {
    'wavendb_url': 'https://wavendb.com',
    'wavendb_uris_to_analyse': {
      'All Page 1': 'page=1&version=3',
      # 'All Page 2': 'page=2&version=3',
      # 'All Page 3': 'page=3&version=3',
      # 'Iop': 'page=1&god=1&version=3',
      # 'Crâ': 'page=1&god=2&version=3',
      # 'Eniripsa': 'page=1&god=3&version=3',
      # 'Sram': 'page=1&god=6&version=3',
      # 'Xélor': 'page=1&god=7&version=3',
      # 'Sacri': 'page=1&god=8&version=3',
      # 'Bouvaloir Orok': 'page=1&weapon=497&version=3',
      # 'Scalpel Apostruker': 'page=1&weapon=637&version=3',
      # 'Aiguille Pikuxala': 'page=1&weapon=945&version=3',
      # 'Écorcheur Shugen': 'page=1&weapon=36&version=3',
      # 'Lame Voracius': 'page=1&weapon=202&version=3',
      # 'Synchronisateur Tako': 'page=1&weapon=490&version=3',
    },
    'public': 'public',
    'pages': 'pages',
    'public_pages': 'public/pages',
    'data_wavendb': 'data_wavendb',
    'max_items': 20,
    'max_builds_per_equipment': 5,
    'max_build_name_length': 35,
    'type': {
      1: {
        'id': 'anneaux',
        'name': 'Anneaux',
      },
      2: {
        'id': 'brassards',
        'name': 'Brassards',
      },
    },
  }
  build_name_max_length_to_print = 22
  builds_per_equipment_to_print = 5
  current_directory = pathlib.Path().resolve()
  home_link_desc = "Home"
  home_text = "WavenTop"
  github_url="https://github.com/developper001/waventop"
  css = f'''
    table, th, td {{
      border: 1px solid grey;
    }}
    table {{
      border-collapse: collapse;
      margin-bottom: 20px;
    }}
    a {{
      text-decoration: none;
    }}
    a:link, a:visited {{
      color: blue;
    }}
    a:hover {{
      color: red;
    }}
    .a_selected {{
      font-weight: bold;
    }}
    .rarity_img {{
      max-width: 55px;
      height: auto;
    }}
    .stuff_img {{
      max-width: 55px;
      height: auto;
      position: absolute;
    }}
    .stuff_with_img {{
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
  '''

  def generate_site_description(self, tag, text, current_uri):
    with tag('div', id='top'):
      text("- ")
      with tag('b'):
        text("Waventop")
      text(" is an opensource website used to find which item is valuable based on Wavendb top builds.")
    with tag('div'):
      text("- Use same query parameter convention as")
      with tag('a', target='_blank', rel='noopener noreferrer', title="wavendb", href=f"{self.config['wavendb_url']}"):
        text(f"{self.config['wavendb_url']}")
    with tag('div'):
      text("- ")
      with tag('b'):
        text("Open source")
      text("github code at")
      with tag('a', target='_blank', rel='noopener noreferrer', title="github", href=f"{self.github_url}"):
        text(f"{self.github_url}")
    with tag('div'):
      text(f"- Last update date : ")
      with tag('b'):
        text(f"{datetime.today().strftime('%Y-%m-%d')}")

  def generate_menus(self, tag, text, current_uri, is_index):
    with tag('div', id='menu'):
      # Index
      a_class = 'a_selected' if is_index else ''
      a_href = f"index.html" if is_index else f"../index.html"
      with tag('a', klass=a_class, href=a_href):
        text(self.home_link_desc)
      # Pages
      wavendb_uris_to_analyse = self.config['wavendb_uris_to_analyse']
      for uri_menu_desc in wavendb_uris_to_analyse:
        uri_menu = wavendb_uris_to_analyse[uri_menu_desc]
        a_class = 'a_selected' if uri_menu == current_uri else ''
        a_href = f"{self.config['pages']}/{uri_menu}.html" if is_index else f"{uri_menu}.html"
        with tag('a', klass=a_class, href=a_href):
          text(uri_menu_desc)

  def generate_content(self, tag, text, items):
    for type in self.config['type']:
      with tag('table', id='table'):
        with tag('tbody'):
          item_count = 0
          for item in items:
            if item['stats'][0]['equipements']['type'] != type:
              continue
            if item_count >= self.config['max_items']:
                continue
            item_count += 1
            with tag('tr'):
              # Stuff
              with tag('td'):
                with tag('div', klass='stuff_with_img'):
                  with tag('img', src=f"{self.config['wavendb_url']}/img/equipment/{item['details']['rarity']}.png.webp", klass='rarity_img'):
                    text('')
                  with tag('img', src=f"{self.config['wavendb_url']}/img/equipment/{item['details']['img']}.png.webp", klass='stuff_img'):
                    with tag('b'):
                      text(f"{item['nom']} ({item['nb']})")
              # Build
              for stat_index in range(self.config['max_builds_per_equipment']):
                with tag('td'):
                  if stat_index >= len(item['stats']):
                    text('')
                  else:
                    stat = item['stats'][stat_index]
                    build = stat['build']
                    hover_text = f"{build['name']}\n{build['likes_count']} likes\n{build['views']} views\n\n{build['description']}"
                    with tag('a', target='_blank', rel='noopener noreferrer', title=hover_text, href=f"{self.config['wavendb_url']}/builds/show/{build['link']}"):
                      build_name_short = build['name'][:self.config['max_build_name_length']]
                      build_name_nospaces = " ".join(build_name_short.split())
                      text(build_name_nospaces)

  def generate_header(self, tag, text, doc):
    with tag('head'):
      with tag('meta', charset="utf-8"):
        text('')
      with tag('title'):
        text(self.home_text)
      with tag('style'):
        doc.asis(self.css)

  def generate_html(self, html_filename, doc):
    html = indent(doc.getvalue(), indent_text = True)
    with open(f"{html_filename}.html", "w", encoding="utf-8") as file:
      file.write(html)

  def generate_static_web_page(self, items, uri):
    doc, tag, text = Doc().tagtext()
    with tag('html'):
      self.generate_header(tag, text, doc)
      with tag('body'):
        self.generate_menus(tag, text, uri, False)
        self.generate_content(tag, text, items)
        self.generate_site_description(tag, text, uri)
    self.generate_html(f"{self.config['public_pages']}/{uri}", doc)

  def generate_index_html(self):
    uri='index'
    doc, tag, text = Doc().tagtext()
    with tag('html'):
      self.generate_header(tag, text, doc)
      with tag('body'):
        self.generate_menus(tag, text, uri, True)
        with tag('h3'):
          text(self.home_text)
        self.generate_site_description(tag, text, uri)
    self.generate_html(f"{self.config['public']}/{uri}", doc)

  def update_stats(self, build, all_equipments, stats):
    for equipement in build["equipments"]:
      equipement_id = equipement["id"]
      equipement_join = [e for e in all_equipments if e['id'] == equipement_id]
      s = {
        'build': build,
        'equipements': equipement_join[0] if (len(equipement_join) >= 1) else None,
        'companions': build["companions"],
      }
      if equipement_id in stats:
        stats[equipement_id].append(s)
      else:
        stats[equipement_id] = [s]

  def print(self, items, nb_to_print, item_type):
    print(f"\nTop {nb_to_print} {item_type} :")
    for item in items[:nb_to_print]:
      stat_details = ''
      for stat in item['stats'][:self.builds_per_equipment_to_print]:
        build = stat['build']
        build_name_short = stat['build_name'][:self.build_name_max_length_to_print]
        build_name_nospaces = " ".join(build_name_short.split())
        stat_details += f"({build['god_id']} {build['likes_count']} {build['views']}) {build_name_nospaces} "
      print(f" [{item['nb']}] {item['nom']}: {stat_details}")

  def generate_results(self, d):
    # Read data
    props = d['props']
    builds = props['builds']['data']
    all_equipments = props['equipments']
    # Builds
    stats = {}
    for build in builds:
      self.update_stats(build, all_equipments, stats)
    # Sort stats
    res = []
    for equipement_id, statistic in stats.items():
      statistic.sort(key=lambda val: -val['build']['likes_count']) # Sort by likes, used by print
      res.append({
        'nb': len(statistic),
        'nom': statistic[0]['equipements']['name_fr'],
        'details': statistic[0]['equipements'],
        'stats': statistic
      })
    res.sort(key=lambda val: -len(val['stats']))
    return res

  def print_console(self, res):
    # Split equipements by type
    self.anneaux = [x for x in res if x['stats'][0]['equipements']['type'] == 1]
    self.brassards = [x for x in res if x['stats'][0]['equipements']['type'] == 2]
    # View results
    self.print(self.anneaux, 10, "Anneaux")
    self.print(self.brassards, 10, "Brassards")
    print("\n")

  def read_from_old_file(self, old_file_path):
    with open(old_file_path, encoding="utf-8") as f:
      d = json.load(f)
    return d

  def request_wavendb_for_data(self, uri, save_wavendb_file=False):
    # Request url
    headers = {
      'content-type': 'application/json',
      'Accept-Charset': 'UTF-8',
    }
    url = f"{self.config['wavendb_url']}/builds?{uri}"
    r = requests.get(url=url, headers=headers)
    r.raise_for_status()
    text = r.text
    pq = PyQuery(text)
    tag = pq('div#app')
    data_page = tag.attr('data-page')
    # Parse data_page to json
    d = json.loads(data_page)
    # Save a file
    if save_wavendb_file:
      with open(f"{self.config['data_wavendb']}/{uri}.json", "w") as file:
          file.write(json.dumps(d, indent=2))
    return d

  def remove_file(self, path, filename):
      file_path = os.path.join(path, filename)
      try:
          if os.path.isfile(file_path) or os.path.islink(file_path):
              os.unlink(file_path)
          elif os.path.isdir(file_path):
              shutil.rmtree(file_path)
      except Exception as e:
          print('Failed to delete %s. Reason: %s' % (file_path, e))

  def remove_all_files_in_folder(self, path):
    for filename in os.listdir(path):
      self.remove_file(path, filename)

  def clean_old_data(self):
    self.remove_all_files_in_folder(self.config['data_wavendb'])
    self.remove_all_files_in_folder(self.config['public_pages'])
    self.remove_file(self.current_directory, f"{self.config['public']}/index.html")

  def run(self):
    self.clean_old_data()
    wavendb_uris_to_analyse = self.config['wavendb_uris_to_analyse']
    print(f"** index.html")
    self.generate_index_html()
    for uri_desc in wavendb_uris_to_analyse:
      print(f"* {uri_desc}")
      uri = wavendb_uris_to_analyse[uri_desc]
      d = self.request_wavendb_for_data(uri, save_wavendb_file=False)
      # d = self.read_from_old_file(f"{self.config['data_wavendb']}/{uri}.json")
      res = self.generate_results(d)
      # self.print_console(res)
      self.generate_static_web_page(res, uri)

w = WavenDbTop()
w.run()
