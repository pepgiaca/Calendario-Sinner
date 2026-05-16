# Calendario auto-aggiornante Jannik Sinner

Feed generato automaticamente in `docs/sinner.ics`.

## URL da usare in Apple Calendario

Dopo aver attivato GitHub Pages:

`https://TUO-USERNAME.github.io/NOME-REPO/sinner.ics`

## Configurazione rapida

1. Crea un repository GitHub pubblico, per esempio `sinner-calendar`.
2. Carica questi file nel repository.
3. Vai su **Settings → Pages**.
4. In **Build and deployment**, scegli:
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/docs**
5. Vai su **Actions** e abilita i workflow se richiesto.
6. Apri il workflow **Aggiorna calendario Sinner** e premi **Run workflow**.
7. Iscriviti al calendario dall’iPhone usando l’URL Pages.

## Nota

Il feed usa dati SofaScore non ufficiali. Se SofaScore cambia gli endpoint, lo script va aggiornato.
