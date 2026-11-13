# Android Auto értesítések

Home Assistant egyedi integráció: a kiválasztott telefonra menő **minden** Home Assistant értesítés megjelenik **Android Autón** is.

Az integráció nem küld külön értesítést, és nem duplikál semmit. Mielőtt a HA kiküldené az értesítést a Companion appnak, beleteszi a `car_ui: true` kapcsolót. Ettől jelenik meg az értesítés az autóban is. Mindegy, ki küldi az értesítést: lehet automatizálás, a Sentient, egy integráció, a `notify.mobile_app_*` szolgáltatás vagy a telefon `notify.*` entitása.

## Telepítés

1. HACS → ⋮ → **Egyéni tárolók** → URL: `https://github.com/suncy1983-hash/android-auto-notify`, típus: **Integráció**.
2. Telepítsd az **Android Auto értesítések** integrációt, majd indítsd újra a Home Assistantot.
3. **Beállítások → Eszközök és szolgáltatások → Integráció hozzáadása → Android Auto értesítések**, majd válaszd ki a telefont.

## Beállítások

- **Kizárt szavak:** vesszővel elválasztva. Ha egy értesítés címében vagy szövegében szerepel valamelyik, az nem jelenik meg az autóban, a telefonon viszont igen.
- Ha egy értesítésben a küldő maga állítja be a `car_ui: false` értéket, az integráció azt nem írja felül.
- A Companion app parancsait (`clear_notification`, `command_*`, `TTS` stb.) nem módosítja.

## A telefonon

- **HA Companion app → Beállítások → Android Auto:** legyen bekapcsolva.
- **Android Auto beállításai:** a Home Assistant értesítései legyenek engedélyezve.

## Megjegyzés

Az integráció a `mobile_app` belső függvényeit csomagolja be (`PushChannel.async_send_notification` és `mobile_app.notify._send_message`). Ha egy HA-frissítés ezeket megváltoztatja, az értesítések továbbra is megérkeznek a telefonra, legfeljebb az autóban nem jelennek meg, amíg az integrációt nem frissítjük. A hibát a HA naplójában `android_auto_notify` néven keresd.
