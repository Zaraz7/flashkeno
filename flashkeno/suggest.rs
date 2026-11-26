use std::collections::HashMap;
use std::env;
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use std::process::Command;

const MAX_POST_BYTES: usize = 65536; // 64 КБ

const FORM_TEMPLATE: &str = r#######"<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Fлешкино: предложить сайт</title>
<meta name="robots" content="follow">
<meta name="keywords" content="flashkeno, fлешкино, ru, ру, indieweb">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {width:80ch; margin:auto;background-color:#FFF;color:#222;font-family:'Courier New',Courier,monospace;}
p, pre, code {margin:0;font-family:'Courier New',Courier,monospace;font-size:16px;}
pre {line-height:1}
th {background-color:#888;color:#FFF}
input[type="submit"]{border: 0;border-radius: 1px;background-color: #24F;color:#FFF;margin-bottom:1ch;}
input[type="submit"]:disabled{background-color: #FFF;color:#222;}
input[type="text"], input[type="url"], input[type="email"] {
  background-color: #FFF;
  color: #222;
  border-style: none none solid none;
  border-color: #222;
}
.ascii{font-size:70%;line-height:0.9;}
.disabled{pointer-events:none;color: #888888;}
.err{color:#C00;font-weight:bold;margin:1ch 0;}
a #cipher {text-decoration: none;height:28ch;}
.footer{font-style:italic;margin-bottom: 2ch;}
img{width:88px;height:31px;image-rendering:pixelated;}
.name{vertical-align:top;text-align:center;}

.radio {display: block;cursor: pointer;}
.radio input {position: absolute;opacity: 0;}
.radio span::before {content: "[ ] ";white-space: pre;}
.radio input:checked + span::before {content: "[*] ";}
.radio input:focus-visible + span {outline: 1px dotted currentColor;outline-offset: 2px;}

@media (max-width:770px) {
body {width:auto;}
p{margin-left: 5px;}
.fr, .fc {display:none;}
.art-table td, .art-table th {width:auto;}}
@media (prefers-color-scheme: dark){
body {background-color:#222;color:#FFF;}
a {color:#4AF;}
.err{color:#F66;}
input[type="text"], input[type="url"], input[type="email"] {
  background-color: #222;
  color: #FFF;
  border-color: #FFF;
}
input[type="submit"]:disabled{background-color:#222;color:#FFF;}}
</style>
</head>
<body>
<center>
<pre class="ascii" content="noindex, nofollow">
  
   ___   ### __________________________________________ 
  |    ####/                                           |
  |   ##'    ,#  /##, #  #  #  #  #/ #   #  #  # .##,  |
  |   ##    #"# /#  # #  #  #  # #/  #  ##  #  # #  #  |
      ##    # # ####' #  #  # ###   #  ,#' /###/ #  #  |
   /######/ # # #    // // // #  #  #  ##  #  #  #  #  |
      ##   #' # "##' #######  #   # ##" #  #  #  "##'  |
     ##' ______________________________________________|
  /###'                                               
  ##'    ${Каталог русскоговорящих || СНГ инди сайтов}
  
</pre>
<p> <a href="/">[Главная]</a> <a href="{{SCRIPT_URL}}">[Предложить]</a> <a href="/guestbook.html">[Гостевая книга]</a></p>
</center>
<hr>
{{ERROR_BLOCK}}
<p>У вас есть что предложить? Или же ваш <i>знакомый</i> имеет свой сайтец? Тогда заполните эту форму:<br></p>
<form action="{{SCRIPT_URL}}" method="POST">
   <label for="name">Название*:</label><br>
   <input type="text" name="name" value="{{NAME}}" required><br>
   <label for="url">Ссылка(и) на сайт*:</label><br>
   <textarea name="url" rows="3" cols="64" placeholder="https://основной-адрес-сайта
http://дополнительный-адрес/~если_есть" required>{{URL}}</textarea><br>
   <label for="button">Ссылка на кнопку (если есть):</label><br>
   <input type="url" name="button" value="{{BUTTON}}"><br>
   <label for="about">Описание*:</label><br>
   <textarea name="about" rows="3" cols="64" placeholder="Введите текст..." required>{{ABOUT}}</textarea><br>
   <fieldset>
      <legend>Тип</legend>
      
      <label class="radio">
         <input type="radio" name="type_id" value="1" {{CHECKED_1}}/>
         <span aria-hidden="true"></span>персональный сайт
      </label>
      <label class="radio">
         <input type="radio" name="type_id" value="2" {{CHECKED_2}}/>
         <span aria-hidden="true"></span>соцсеть
      </label>
      <label class="radio">
         <input type="radio" name="type_id" value="3" {{CHECKED_3}}/>
         <span aria-hidden="true"></span>форум
      </label>
      <label class="radio">
         <input type="radio" name="type_id" value="165" {{CHECKED_165}}/>
         <span aria-hidden="true"></span>библиотека
      </label>
      <label class="radio">
         <input type="radio" name="type_id" value="157" {{CHECKED_157}}/>
         <span aria-hidden="true"></span>другое
      </label>
    </fieldset><br>
   <label for="email">Опционально можете написать свой email, чтобы узнать о статусе рассмотрения заявки:</label>
   <input type="email" name="email" placeholder="example@mail.su" value="{{EMAIL}}"><br><br>

   <label for="captcha_answer">Решите пример*:</label><br>
   <pre>{{CAPTCHA_ART}}</pre><br>
   <input type="hidden" name="captcha_token" value="{{CAPTCHA_TOKEN}}">
   <input type="text" name="captcha_answer" autocomplete="off" required><br><br>

   <input type="submit">
</form>
<center>
<hr>
<p class="footer">Администрируется <a href="//zaraz7.narod.ws" target="_blank">Zaraz7</a>.</p>
</center>
</body>
</html>"#######;

struct FormData {
    name: String,
    url: String,
    button: String,
    about: String,
    type_id: String,
    email: String,
    captcha_token: String,
    captcha_answer: String,
}

impl Default for FormData {
    fn default() -> Self {
        Self {
            name: String::new(),
            url: String::new(),
            button: String::new(),
            about: String::new(),
            type_id: "1".to_string(),
            email: String::new(),
            captcha_token: String::new(),
            captcha_answer: String::new(),
        }
    }
}

fn html_escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}

fn url_decode(s: &str) -> String {
    let bytes = s.as_bytes();
    let mut out = Vec::with_capacity(bytes.len());
    let mut i = 0;
    while i < bytes.len() {
        match bytes[i] {
            b'+' => {
                out.push(b' ');
                i += 1;
            }
            b'%' if i + 2 < bytes.len() => {
                if let Ok(hex) = std::str::from_utf8(&bytes[i + 1..i + 3]) {
                    if let Ok(val) = u8::from_str_radix(hex, 16) {
                        out.push(val);
                        i += 3;
                        continue;
                    }
                }
                out.push(b'%');
                i += 1;
            }
            b => {
                out.push(b);
                i += 1;
            }
        }
    }
    String::from_utf8_lossy(&out).into_owned()
}

fn parse_form(body: &str) -> HashMap<String, String> {
    body.split('&')
        .filter_map(|pair| {
            let mut parts = pair.splitn(2, '=');
            let k = parts.next()?;
            let v = parts.next().unwrap_or("");
            Some((url_decode(k), url_decode(v)))
        })
        .collect()
}

fn send_headers() {
    print!("Content-Type: text/html; charset=utf-8\r\n");
    print!("Cache-Control: no-store\r\n\r\n");
}

fn render_form(exe_dir: &Path, script_url: &str, data: &FormData, error: Option<&str>) {
    send_headers();

    let captcha_bin = exe_dir.join("captcha.cgi");
    let output = match Command::new(&captcha_bin).arg("--generate").output() {
        Ok(o) if o.status.success() => o,
        Ok(o) => {
            let err = String::from_utf8_lossy(&o.stderr);
            print!("<p>Ошибка генерации капчи: {}</p>", html_escape(&err));
            return;
        }
        Err(e) => {
            print!("<p>Не удалось запустить captcha.cgi: {}</p>", html_escape(&e.to_string()));
            return;
        }
    };

    let stdout = String::from_utf8_lossy(&output.stdout);
    let mut lines = stdout.lines();
    let token = lines.next().unwrap_or("").trim();
    let art = lines.collect::<Vec<_>>().join("\n");

    let error_block = match error {
        Some(msg) => format!(r#"<p class="err">{}</p>"#, html_escape(msg)),
        None => String::new(),
    };

    let checked = |id: &str| if data.type_id == id { "checked" } else { "" };

    let page = FORM_TEMPLATE
        .replace("{{SCRIPT_URL}}", &html_escape(script_url))
        .replace("{{ERROR_BLOCK}}", &error_block)
        .replace("{{NAME}}", &html_escape(&data.name))
        .replace("{{URL}}", &html_escape(&data.url))
        .replace("{{BUTTON}}", &html_escape(&data.button))
        .replace("{{ABOUT}}", &html_escape(&data.about))
        .replace("{{EMAIL}}", &html_escape(&data.email))
        .replace("{{CHECKED_1}}", checked("1"))
        .replace("{{CHECKED_2}}", checked("2"))
        .replace("{{CHECKED_3}}", checked("3"))
        .replace("{{CHECKED_165}}", checked("165"))
        .replace("{{CHECKED_157}}", checked("157"))
        .replace("{{CAPTCHA_TOKEN}}", &html_escape(token))
        .replace("{{CAPTCHA_ART}}", &html_escape(&art));

    print!("{}", page);
}

fn render_success(script_url: &str, suggestion_id: &str) {
    send_headers();
    print!(
        r#"<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Заявка отправлена</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{width:80ch; margin:auto;background-color:#FFF;color:#222;font-family:'Courier New',Courier,monospace;}}
@media (max-width:770px) {{body {{width:auto;margin:0 5px;}}}}
@media (prefers-color-scheme: dark){{body {{background-color:#222;color:#FFF;}} a {{color:#4AF;}}}}
</style>
</head>
<body>
<h1>Спасибо за заявку!</h1>
<p>Ваша заявка принята и будет рассмотрена в ближайшее время.<br>
Номер заявки: {}</p>
<p><a href="{}">Новая заявка</a> | <a href="/">Вернуться на главную</a></p>
</body>
</html>"#,
        html_escape(suggestion_id),
        html_escape(script_url)
    );
}

fn find_python(exe_dir: &Path) -> PathBuf {
    let venv_py = exe_dir.join("../../.venv/bin/python3");
    if venv_py.exists() {
        venv_py
    } else {
        PathBuf::from("python3")
    }
}

fn handle_post(exe_dir: &Path, script_url: &str) {
    let content_len: usize = env::var("CONTENT_LENGTH")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(0)
        .min(MAX_POST_BYTES);

    let mut buf = vec![0u8; content_len];
    let _ = io::stdin().read_exact(&mut buf);
    let body = String::from_utf8_lossy(&buf);
    let map = parse_form(&body);

    let get = |k: &str| map.get(k).cloned().unwrap_or_default();
    let data = FormData {
        name: get("name"),
        url: get("url"),
        button: get("button"),
        about: get("about"),
        type_id: map.get("type_id").cloned().unwrap_or_else(|| "1".to_string()),
        email: get("email"),
        captcha_token: get("captcha_token"),
        captcha_answer: get("captcha_answer"),
    };

    if data.name.trim().is_empty() || data.url.trim().is_empty() || data.about.trim().is_empty() {
        render_form(exe_dir, script_url, &data, Some("Заполните все обязательные поля."));
        return;
    }

    // Проверка капчи
    let captcha_bin = exe_dir.join("captcha.cgi");
    let captcha_ok = Command::new(&captcha_bin)
        .args(["--verify", &data.captcha_token, &data.captcha_answer])
        .status()
        .map(|s| s.success())
        .unwrap_or(false);

    if !captcha_ok {
        render_form(
            exe_dir,
            script_url,
            &data,
            Some("Неверная или просроченная капча. Попробуйте снова."),
        );
        return;
    }

    // Запись в БД через ../../lib/database.py
    let client_ip = env::var("REMOTE_ADDR").unwrap_or_else(|_| "None".to_string());
    let client_agent = env::var("HTTP_USER_AGENT").unwrap_or_else(|_| "Чудоюдо".to_string());

    let db_script = exe_dir.join("../../lib/database.py");
    let python_bin = find_python(exe_dir);

    let db_out = Command::new(&python_bin)
        .arg(&db_script)
        .args([
            &data.email,
            &data.name,
            &data.url,
            &data.button,
            &data.about,
            &data.type_id,
            &client_ip,
            &client_agent,
        ])
        .output();

    match db_out {
        Ok(o) if o.status.success() => {
            let suggestion_id = String::from_utf8_lossy(&o.stdout).trim().to_string();
            render_success(script_url, &suggestion_id);
        }
        Ok(o) => {
            let err = String::from_utf8_lossy(&o.stderr);
            render_form(
                exe_dir,
                script_url,
                &data,
                Some(&format!("Ошибка сохранения заявки: {}", err.trim())),
            );
        }
        Err(e) => {
            render_form(
                exe_dir,
                script_url,
                &data,
                Some(&format!("Не удалось запустить database.py: {}", e)),
            );
        }
    }
}

fn main() {
    let exe = env::current_exe().unwrap_or_default();
    let exe_dir = exe.parent().unwrap_or_else(|| Path::new("."));
    let script_url = env::var("SCRIPT_NAME").unwrap_or_else(|_| "/cgi-bin/suggest.cgi".to_string());

    let method = env::var("REQUEST_METHOD").unwrap_or_else(|_| "GET".to_string());
    if method.eq_ignore_ascii_case("POST") {
        handle_post(exe_dir, &script_url);
    } else {
        render_form(exe_dir, &script_url, &FormData::default(), None);
    }
}