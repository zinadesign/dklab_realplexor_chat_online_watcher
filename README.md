Назначение
----------
Нужен для мониторинга статусов пользователей в чате использующем сервер Dklab realplexor http://dklab.ru/lib/dklab_realplexor/.

Например нам нужно показать вновь зашедшего пользователя в списке кто онлайн. 
Этот скрипт отправит в канал {конфиг.online_channel} информацию о пользователе и его статусе online/offline
Получаем в js сообщение  и добавляем профиль в список кто онлайн

Установка
---------
клонируем репозиторий в /opt
```
cd /opt
git clone https://github.com/zinadesign/dklab_realplexor_chat_online_watcher.git
```
копируем конфиг и редактируем его
```
cp /opt/dklab_realplexor_chat_online_watcher/conf/chat_online.sample.json /opt/dklab_realplexor_chat_online_watcher/conf/chat_online.json
```
Ставим в автозапуск. В качестве init скрпта использую System V init script так как на данный момент хорошо поддерживается большинством дистрибутивов
```
cp /opt/dklab_realplexor_chat_online_watcher/conf/chat_online_watcher_init /etc/init.d/dklab_realplexor_chat_online_watcher
chmod +x /etc/init.d/dklab_realplexor_chat_online_watcher
Debian based
update-rc.d dklab_realplexor_chat_online_watcher defaults
OR RED HAT based
chkconfig --add dklab_realplexor_chat_online_watcher
chkconfig dklab_realplexor_chat_online_watcher on
```
Стартуем
```
service dklab_realplexor_chat_online_watcher start
```
Стопим
```
service dklab_realplexor_chat_online_watcher stop
```