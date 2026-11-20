from __future__ import annotations

from typing import Any

SUPPORTED = ("en", "sv")
DEFAULT = "en"
COOKIE_NAME = "samsyn_lang"

MOCK = {"en": "(mock)", "sv": "(test)"}

LABELS: dict[str, dict[str, dict[str, str]]] = {
    "en": {
        "kind": {
            "one_to_one": "1:1 call",
            "customer_service": "Customer service",
            "in_person": "In person",
        },
        "state": {
            "waiting": "Waiting",
            "ready": "Ready",
            "confirming": "Confirming",
            "verified": "Verified",
            "mismatch": "Mismatch",
            "expired": "Expired",
            "cancelled": "Cancelled",
        },
        "role": {
            "initiator": "Initiator",
            "responder": "Responder",
            "host": "Host",
            "member": "Participant",
        },
        "assurance": {
            "proxy": "Signed in via proxy",
            "eid_auth": "eID verified",
            "eid_sign": "eID signed",
        },
    },
    "sv": {
        "kind": {
            "one_to_one": "1:1-samtal",
            "customer_service": "Kundservice",
            "in_person": "På plats",
        },
        "state": {
            "waiting": "Väntar",
            "ready": "Redo",
            "confirming": "Bekräftar",
            "verified": "Verifierad",
            "mismatch": "Avvikelse",
            "expired": "Utgången",
            "cancelled": "Avbruten",
        },
        "role": {
            "initiator": "Initiativtagare",
            "responder": "Deltagare",
            "host": "Värd",
            "member": "Deltagare",
        },
        "assurance": {
            "proxy": "Inloggad via proxy",
            "eid_auth": "eID-verifierad",
            "eid_sign": "eID-signerad",
        },
    },
}

# English strings are the keys. This dictionary only needs the Swedish text.
SV: dict[str, str] = {
    # Global / navigation
    "Skip to content": "Hoppa till innehållet",
    "Home": "Hem",
    "How it works": "Så fungerar det",
    "Safety": "Säkerhet",
    "Sign out": "Logga ut",
    "Language": "Språk",
    "Switch theme": "Byt tema",
    "Switch to light theme": "Byt till ljust tema",
    "Switch to dark theme": "Byt till mörkt tema",
    "Verify who you're talking to": "Verifiera vem du pratar med",
    "Verify who you're talking to.": "Verifiera vem du pratar med.",
    "No trackers. No password login.": "Inga spårare. Ingen lösenordsinloggning.",
    "JavaScript is required for the live verification session.": "JavaScript krävs för den aktiva verifieringen.",
    "Main": "Huvudmeny",
    "Mobile": "Mobilmeny",
    # Home
    "Mutual verification": "Ömsesidig verifiering",
    "Verify who you're talking to.": "Verifiera vem du pratar med.",
    "Create a short verification, share the link, and compare the same code together. It takes about a minute.": "Skapa en kort verifiering, dela länken och jämför samma kod tillsammans. Det tar ungefär en minut.",
    "Start a verification": "Starta en verifiering",
    "Create a link for the person you're talking to.": "Skapa en länk till personen du pratar med.",
    "Start verification": "Starta verifiering",
    "Options": "Alternativ",
    "Type": "Typ",
    "1:1 call": "1:1-samtal",
    "Customer service": "Kundservice",
    "In person": "På plats",
    "What is it for?": "Vad gäller det?",
    "optional": "valfritt",
    "e.g. Apartment viewing": "t.ex. bostadsvisning",
    "Expires": "Gäller i",
    "5 minutes": "5 minuter",
    "10 minutes": "10 minuter",
    "15 minutes": "15 minuter",
    "Personal number": "Personnummer",
    "Full number": "Fullständigt nummer",
    "Masked": "Maskerat",
    "Full personal numbers are sensitive. They are shown only inside this verification.": "Fullständiga personnummer är känsliga. De visas bara inne i den här verifieringen.",
    "Join a verification": "Gå med i en verifiering",
    "Paste the link you received.": "Klistra in länken du fick.",
    "Paste invitation link": "Klistra in inbjudningslänk",
    "Continue": "Fortsätt",
    "The link works once and expires quickly.": "Länken fungerar en gång och går ut snabbt.",
    "Recent verifications": "Senaste verifieringar",
    "Waiting for the other person": "Väntar på den andra personen",
    "No verifications yet.": "Inga verifieringar ännu.",
    "Share the link": "Dela länken",
    "Compare the code": "Jämför koden",
    "Both confirm": "Båda bekräftar",
    "Share": "Dela",
    "Compare": "Jämför",
    "Verify": "Verifiera",
    "Done": "Klart",
    "Invite": "Bjud in",
    "Your code": "Din kod",
    "Your code appears when the other person joins.": "Din kod visas när den andra personen går med.",
    "You will each get your own code to read aloud.": "Ni får varsin kod som ni läser högt.",
    "You each get your own code.": "Ni får varsin kod.",
    "Each of you reads your code aloud; the other enters it.": "Ni läser varsin kod högt; den andra anger den.",
    "Share the link, not the codes. Anyone on the call can hear a code when it is read aloud; the codes are not passwords and expire.": "Dela länken, inte koderna. Alla i samtalet kan höra en kod när den läses högt; koderna är inte lösenord och går ut.",
    "Verify each other's codes.": "Verifiera varandras koder.",
    "Read your code aloud": "Läs din kod högt",
    "Read your code aloud.": "Läs din kod högt.",
    "Read your own code aloud to {name}.": "Läs din egen kod högt för {name}.",
    "Enter the code {name} reads to you.": "Ange koden som {name} läser upp.",
    "When both codes are verified, you are done.": "När båda koderna är verifierade är ni klara.",
    "Anyone on the call can hear the codes. They are not passwords and expire. Do not text or email them.": "Alla i samtalet kan höra koderna. De är inte lösenord och går ut. Skicka dem inte i SMS eller e-post.",
    "{name} has verified your code.": "{name} har verifierat din kod.",
    "Waiting for {name} to verify your code.": "Väntar på att {name} ska verifiera din kod.",
    "You verified {name}'s code.": "Du har verifierat koden från {name}.",
    "Keep this page open until the other person verifies your code.": "Håll sidan öppen tills den andra personen har verifierat din kod.",
    "Enter {name}'s code": "Ange koden från {name}",
    "6 digits": "6 siffror",
    "Verify their code": "Verifiera koden",
    "Both codes were verified. A receipt is available.": "Båda koderna verifierades. Ett kvitto finns.",
    "Your code was verified. Waiting for the other person.": "Din kod verifierades. Väntar på den andra personen.",
    "Enter the code they read to you.": "Ange koden som personen läser upp.",
    "Both codes were verified.": "Båda koderna verifierades.",
    "Invitation link": "Inbjudningslänk",
    "Create a short verification, share the link, and verify each other with your own codes. It takes about a minute.": "Skapa en kort verifiering, dela länken och verifiera varandra med varsin kod. Det tar ungefär en minut.",
    "Each reads a code": "Varsin kod läses högt",
    "Both verify": "Båda verifierar",
    "Only continue if you expected this call. The codes confirm the session and the accounts; they do not prove the voice on the call.": "Fortsätt bara om du förväntade dig samtalet. Koderna bekräftar sessionen och kontona; de bevisar inte rösten i samtalet.",
    "You will see their name and get your own code. You will each read your code aloud and enter the other's code.": "Du ser personens namn och får din egen kod. Ni läser varsin kod högt och anger den andras kod.",
    "Both people read their own code aloud and the other verified it.": "Båda personerna läste sin egen kod högt och den andra verifierade den.",
    "Each person saw the other's name and verified the code read aloud.": "Varje person såg den andras namn och verifierade koden som lästes högt.",
    "You share an invitation link, both join, and each of you reads your own code aloud for the other to verify. It takes about a minute.": "Du delar en inbjudningslänk, båda går med och ni läser varsin kod högt så att den andra kan verifiera den. Det tar ungefär en minut.",
    "The other person opens the link and signs in. You each get your own code.": "Den andra personen öppnar länken och loggar in. Ni får varsin kod.",
    "Read your own 6 digits and 3 words on the call. The other person enters your code. Then they read theirs and you enter it. Do not text or email the codes.": "Läs dina egna 6 siffror och 3 ord i samtalet. Den andra personen anger din kod. Sedan läser personen sin kod och du anger den. Skicka inte koderna i SMS eller e-post.",
    "When each person has verified the other's code, the verification is complete and a receipt is created.": "När båda har verifierat den andras kod är verifieringen klar och ett kvitto skapas.",
    "Share the link, not the codes.": "Dela länken, inte koderna.",
    "Each person has a different code. Do not send the codes by message.": "Varje person har en egen kod. Skicka inte koderna i meddelanden.",
    "Read your code aloud only after both of you have joined.": "Läs din kod högt först när båda har gått med.",
    "Who can hear the codes": "Vem som kan höra koderna",
    "Anyone on the call can hear them.": "Alla i samtalet kan höra dem.",
    "The codes are not passwords. They are short-lived checks that you are in the same session.": "Koderna är inte lösenord. De är kortlivade kontroller att ni är i samma session.",
    "Do not read them to someone who called you first, and do not post them.": "Läs inte upp dem för någon som ringde dig först, och publicera dem inte.",
    "In a group call, other people can hear the codes. The app cannot detect a silent listener. For sensitive calls, use a 1:1 call and check the name.": "I ett gruppsamtal kan andra höra koderna. Appen kan inte upptäcka en tyst lyssnare. Använd ett 1:1-samtal och kontrollera namnet vid känsliga samtal.",
    "Read your own code aloud.": "Läs din egen kod högt.",
    "Enter the code the other person reads to you.": "Ange koden som den andra personen läser upp.",
    "If a name or code is wrong, stop.": "Om ett namn eller en kod inte stämmer, avbryt.",
    "Sensitive": "Känsligt",
    "Waiting": "Väntar",
    "Verified.": "Verifierad.",
    "Do not continue the call.": "Fortsätt inte samtalet.",
    "Hide": "Dölj",
    "Show": "Visa",
    "Share mine": "Dela mitt",
    "Not shared": "Inte delat",
    "Shared full number": "Fullständigt nummer delat",
    "You": "Du",
    "Copy": "Kopiera",
    "other person": "den andra personen",
    "Customer": "Kund",
    "Creating…": "Skapar…",
    "Joining…": "Går med…",
    "Working…": "Arbetar…",
    "Receipt {ref}": "Kvitto {ref}",
    "What to share and what to do": "Vad du delar och vad du gör",
    "Only continue if you expected this call. The code confirms the session and the accounts; it does not prove the voice on the call.": "Fortsätt bara om du förväntade dig samtalet. Koden bekräftar sessionen och kontona; den bevisar inte rösten i samtalet.",
    # Login / dev
    "Sign in": "Logga in",
    "Development mode": "Utvecklingsläge",
    "Choose a test identity.": "Välj en testidentitet.",
    "This page is only for local testing. In production, your secure login identifies you automatically.": "Den här sidan finns bara för lokal testning. I produktion identifierar din säkra inloggning dig automatiskt.",
    "Never expose development mode to the internet.": "Exponera aldrig utvecklingsläget mot internet.",
    "Private individual": "Privatperson",
    "Unknown mock identity.": "Okänd testidentitet.",
    # Join
    "Join verification": "Gå med i verifiering",
    "Verification request": "Verifieringsförfrågan",
    "{name} wants to verify you.": "{name} vill verifiera dig.",
    "Only continue if you expected this call.": "Fortsätt bara om du förväntade dig samtalet.",
    "Never read a code to someone who called you.": "Läs aldrig upp en kod för någon som ringde dig.",
    "Continue only inside this app.": "Fortsätt bara inne i den här appen.",
    "You will see their name and a shared code. Compare the code on the call, then both confirm.": "Du ser personens namn och en gemensam kod. Jämför koden i samtalet och bekräfta sedan tillsammans.",
    "Not now": "Inte nu",
    "You are signed in as {name}.": "Du är inloggad som {name}.",
    "JavaScript is required to join.": "JavaScript krävs för att gå med.",
    # Session (server-rendered shell)
    "Loading verification": "Laddar verifiering",
    "No JavaScript": "Ingen JavaScript",
    "This session is {state}. The live comparison and confirmation need JavaScript. You can still view the receipt if the session is verified.": "Den här sessionen är {state}. Den aktiva jämförelsen och bekräftelsen kräver JavaScript. Du kan fortfarande öppna kvittot om sessionen är verifierad.",
    "Open receipt": "Öppna kvitto",
    "Verification": "Verifiering",
    # Receipt
    "Back": "Tillbaka",
    "Save PDF": "Spara PDF",
    "Verification receipt": "Verifieringskvitto",
    "Verified": "Verifierad",
    "Both people confirmed the same session and each other's identity.": "Båda personerna bekräftade samma session och varandras identitet.",
    "Participants": "Deltagare",
    "This confirms that both accounts joined and confirmed the session. It does not verify the call audio or video.": "Detta bekräftar att båda kontona gick med i och bekräftade sessionen. Det verifierar inte samtalets ljud eller video.",
    # Safety
    "What this app confirms.": "Vad appen bekräftar.",
    "Samsyn confirms that both people joined the same verification and confirmed each other's account. It does not verify the call itself.": "Samsyn bekräftar att båda personerna gick med i samma verifiering och bekräftade varandras konto. Det verifierar inte själva samtalet.",
    "It confirms": "Det bekräftar",
    "Both signed-in accounts joined the same session.": "Båda inloggade konton gick med i samma session.",
    "Both people saw the same name and code.": "Båda personerna såg samma namn och kod.",
    "Both independently confirmed.": "Båda bekräftade oberoende av varandra.",
    "It does not confirm": "Det bekräftar inte",
    "That the voice or video is authentic.": "Att rösten eller videon är äkta.",
    "That a device or account is not compromised.": "Att en enhet eller ett konto inte är komprometterat.",
    "That everyone in a group call is present.": "Att alla i ett gruppsamtal är närvarande.",
    "If the name or code is wrong, stop.": "Om namnet eller koden inte stämmer, avbryt.",
    "Do not continue the call based on this verification. Contact the person or company through a channel you already trust.": "Fortsätt inte samtalet utifrån den här verifieringen. Kontakta personen eller företaget via en kanal du redan litar på.",
    "Back to verification": "Tillbaka till verifieringen",
    # How it works
    "Two people. One short verification.": "Två personer. En kort verifiering.",
    "You share an invitation link, both join, read the same code aloud, and both confirm. It takes about a minute.": "Du delar en inbjudningslänk, båda går med, läser samma kod högt och bekräftar tillsammans. Det tar ungefär en minut.",
    "Share the link": "Dela länken",
    "Start a verification and copy the link. Send it to the person in the call chat, by SMS, or by email. The link works once and expires.": "Starta en verifiering och kopiera länken. Skicka den till personen i samtalets chatt, via SMS eller e-post. Länken fungerar en gång och går ut.",
    "Both join": "Båda går med",
    "The other person opens the link and signs in. You will both see each other's name and the same code.": "Den andra personen öppnar länken och loggar in. Ni ser båda varandras namn och samma kod.",
    "Read the code aloud": "Läs koden högt",
    "Read the 6 digits and 3 words on the call. Do not text or email the code; it must be compared live. Check that the name is the person you expected.": "Läs de 6 siffrorna och 3 orden i samtalet. Skicka inte koden i SMS eller e-post; den måste jämföras live. Kontrollera att namnet är personen du förväntade dig.",
    "Both confirm": "Båda bekräftar",
    "Each person presses Confirm. Only then is the verification complete and a receipt created.": "Varje person trycker på Bekräfta. Först då är verifieringen klar och ett kvitto skapas.",
    "What to share": "Vad du delar",
    "Share the link, not the code.": "Dela länken, inte koden.",
    "Send the invitation link in the call chat, SMS, or email.": "Skicka inbjudningslänken i samtalets chatt, via SMS eller e-post.",
    "The link works once. Do not post it publicly.": "Länken fungerar en gång. Publicera den inte offentligt.",
    "The code is read aloud only after both of you have joined.": "Koden läses högt först när båda har gått med.",
    "Who can hear the code": "Vem som kan höra koden",
    "Anyone on the call can hear it.": "Alla i samtalet kan höra den.",
    "The code is not a password. It is a short-lived check that you are in the same session.": "Koden är inte ett lösenord. Den är en kortlivad kontroll att ni är i samma session.",
    "Do not read it to someone who called you first, and do not post it.": "Läs inte upp den för någon som ringde dig först, och publicera den inte.",
    "In a group call, other people can hear it. The app cannot detect a silent listener. For sensitive calls, use a 1:1 call and check the name.": "I ett gruppsamtal kan andra höra den. Appen kan inte upptäcka en tyst lyssnare. Använd ett 1:1-samtal och kontrollera namnet vid känsliga samtal.",
    "During the verification": "Under verifieringen",
    "What each person should do.": "Vad varje person ska göra.",
    "The person who starts": "Personen som startar",
    "Start a verification.": "Starta en verifiering.",
    "Copy the invitation link and send it to the other person.": "Kopiera inbjudningslänken och skicka den till den andra personen.",
    "Wait for them to join.": "Vänta tills personen går med.",
    "Read the code aloud and press Confirm.": "Läs koden högt och tryck på Bekräfta.",
    "The person who joins": "Personen som går med",
    "Open the invitation link.": "Öppna inbjudningslänken.",
    "Check the name of the person who invited you.": "Kontrollera namnet på personen som bjöd in dig.",
    "Compare the code with them on the call.": "Jämför koden med personen i samtalet.",
    "Press Confirm only if the name and code match.": "Tryck bara på Bekräfta om namnet och koden stämmer.",
    "Press “Something is wrong” and do not continue the call based on this verification. Contact the person or company through a channel you already trust.": "Tryck på ”Något stämmer inte” och fortsätt inte samtalet utifrån den här verifieringen. Kontakta personen eller företaget via en kanal du redan litar på.",
    # Error / auth pages
    "Sign in required": "Inloggning krävs",
    "Open this app through your secure login.": "Öppna appen via din säkra inloggning.",
    "Samsyn uses your existing secure login. If you reached this page directly, return to the app link you were given and sign in there.": "Samsyn använder din befintliga säkra inloggning. Om du kom hit direkt, gå tillbaka till app-länken du fick och logga in där.",
    "Try again": "Försök igen",
    "Error": "Fel",
    "Not found.": "Hittades inte.",
    "Access denied.": "Åtkomst nekad.",
    "Expired.": "Utgången.",
    "Something went wrong.": "Något gick fel.",
    "Method not allowed": "Metoden är inte tillåten",
    "Back to home": "Tillbaka till startsidan",
    "Security model": "Säkerhetsmodell",
    # Session JS
    "Share this verification.": "Dela den här verifieringen.",
    "Compare and confirm.": "Jämför och bekräfta.",
    "Do not continue.": "Fortsätt inte.",
    "Cancelled.": "Avbruten.",
    "Your code": "Din kod",
    "Send this link.": "Skicka den här länken.",
    "Share this link in the call chat. It works once and expires.": "Dela länken i samtalets chatt. Den fungerar en gång och går ut.",
    "The link is no longer available. Start a new verification.": "Länken finns inte längre. Starta en ny verifiering.",
    "Waiting for the other person.": "Väntar på den andra personen.",
    "Share the link below. The verification starts when they join.": "Dela länken nedan. Verifieringen börjar när personen går med.",
    "What happens next": "Vad som händer nu",
    "They open the link and join.": "Personen öppnar länken och går med.",
    "You both see the same name and code.": "Ni ser båda samma namn och kod.",
    "Read the code aloud. Both of you confirm.": "Läs koden högt. Båda bekräftar.",
    "Share the link, not the code. Anyone on the call can hear the code; it is not a password and expires.": "Dela länken, inte koden. Alla i samtalet kan höra koden; den är inte ett lösenord och går ut.",
    "Keep this page open until the result appears.": "Håll sidan öppen tills resultatet visas.",
    "Who is in this session?": "Vilka är med i sessionen?",
    "Read the code aloud.": "Läs koden högt.",
    "What to do": "Vad du ska göra",
    "Check that the name is the person you expected.": "Kontrollera att namnet är personen du förväntade dig.",
    "Both press Confirm.": "Båda trycker på Bekräfta.",
    "Anyone on the call can hear the code. It is not a password and expires. Do not text or email it.": "Alla i samtalet kan höra koden. Den är inte ett lösenord och går ut. Skicka den inte i SMS eller e-post.",
    "Only confirm if the name and code match.": "Bekräfta bara om namnet och koden stämmer.",
    "You confirmed": "Du har bekräftat",
    "And {name} confirmed": "Och {name} har bekräftat",
    "Waiting for {name}": "Väntar på {name}",
    "{name} confirmed": "{name} har bekräftat",
    "{name} has not confirmed yet": "{name} har inte bekräftat än",
    "I see the same code: {code}": "Jag ser samma kod: {code}",
    "I confirm this is the person I am talking to.": "Jag bekräftar att det är personen jag pratar med.",
    "Confirm": "Bekräfta",
    "Something is wrong": "Något stämmer inte",
    "Both people confirmed the same session. A receipt is available.": "Båda personerna bekräftade samma session. Ett kvitto finns.",
    "Save PDF": "Spara PDF",
    "Start another": "Starta en ny",
    "Start a new verification": "Starta en ny verifiering",
    "The code or the person did not match. No receipt was created.": "Koden eller personen stämde inte. Inget kvitto skapades.",
    "This verification expired.": "Verifieringen har gått ut.",
    "The time ran out before both people confirmed.": "Tiden tog slut innan båda bekräftade.",
    "This verification was cancelled.": "Verifieringen avbröts.",
    "No receipt was created.": "Inget kvitto skapades.",
    "This verification is closed.": "Verifieringen är stängd.",
    "Start a new verification.": "Starta en ny verifiering.",
    "Verification code": "Verifieringskod",
    "Expires in": "Går ut om",
    "Copy": "Kopiera",
    "Open as {name}": "Öppna som {name}",
    "Cancel": "Avbryt",
    "Invite link copied.": "Inbjudningslänken kopierades.",
    "Could not copy the link.": "Kunde inte kopiera länken.",
    "Copied.": "Kopierat.",
    "Could not copy.": "Kunde inte kopiera.",
    "Confirmation recorded.": "Bekräftelsen registrerades.",
    "The session was marked as a mismatch.": "Sessionen markerades som avvikande.",
    "Your full personal number is now shared with the other participant.": "Ditt fullständiga personnummer delas nu med den andra deltagaren.",
    "Session cancelled.": "Sessionen avbröts.",
    "What is wrong?": "Vad stämmer inte?",
    "Reporting a mismatch closes the session immediately. No receipt will be created. If you are unsure, keep the session open and compare again.": "Om du rapporterar en avvikelse stängs sessionen direkt. Inget kvitto skapas. Om du är osäker kan du hålla sessionen öppen och jämföra igen.",
    "The code does not match": "Koden stämmer inte",
    "The person is not who I expected": "Personen är inte den jag förväntade mig",
    "Keep the session open": "Håll sessionen öppen",
    "Cancel this session?": "Avbryta sessionen?",
    "The other participant will see that the session was cancelled. No receipt will be created.": "Den andra deltagaren ser att sessionen avbröts. Inget kvitto skapas.",
    "Cancel session": "Avbryt session",
    "Keep it open": "Håll den öppen",
    "Paste an invite link or token.": "Klistra in en inbjudningslänk eller kod.",
    "Could not load this session.": "Kunde inte ladda sessionen.",
    # Errors (English fallback is the key unless overridden below)
    "error.csrf": "Din session kunde inte kontrolleras. Ladda om sidan och försök igen.",
    "error.origin": "Webbadressen är inte tillåten. Kontrollera BASE_URL eller ALLOWED_ORIGINS.",
    "error.rate_limited": "För många försök. Vänta en stund och försök igen.",
    "error.not_found": "Det gick inte att hitta verifieringen.",
    "error.forbidden": "Du har inte åtkomst till den här verifieringen.",
    "error.expired": "Verifieringen har gått ut.",
    "error.used": "Den här inbjudningslänken har redan använts.",
    "error.full": "Verifieringen har redan två deltagare.",
    "error.terminal": "Verifieringen är redan stängd.",
    "error.not_ready": "Båda måste gå med innan ni kan bekräfta.",
    "error.stale_roster": "Deltagarlistan ändrades. Ladda om och bekräfta igen.",
    "error.invalid_input": "Kontrollera uppgifterna och försök igen.",
    "error.invalid_token": "Inbjudningslänken är ogiltig.",
    "error.invalid_code": "Koden stämmer inte. Be personen läsa den igen.",
    "error.invalid_decision": "Ogiltigt val.",
    "error.invalid_roster": "Ogiltig deltagarlista.",
    "error.invalid_json": "Ogiltig begäran.",
    "error.body_too_large": "Begäran är för stor.",
    "error.generic": "Något gick fel. Försök igen.",
}

# English fallback for error codes so the UI never shows "error.csrf".
EN: dict[str, str] = {
    "error.csrf": "Your session check failed. Refresh the page and try again.",
    "error.origin": "This web address is not allowed. Check BASE_URL or ALLOWED_ORIGINS.",
    "error.rate_limited": "Too many attempts. Wait a moment and try again.",
    "error.not_found": "The verification could not be found.",
    "error.forbidden": "You do not have access to this verification.",
    "error.expired": "This verification has expired.",
    "error.used": "This invitation link has already been used.",
    "error.full": "This verification already has two participants.",
    "error.terminal": "This verification is already closed.",
    "error.not_ready": "Both people must join before confirming.",
    "error.stale_roster": "The participant list changed. Refresh and confirm again.",
    "error.invalid_input": "Check the details and try again.",
    "error.invalid_token": "The invitation link is invalid.",
    "error.invalid_code": "The code does not match. Ask the person to read it again.",
    "error.invalid_decision": "Invalid choice.",
    "error.invalid_roster": "Invalid participant list.",
    "error.invalid_json": "Invalid request.",
    "error.body_too_large": "The request is too large.",
    "error.generic": "Something went wrong. Try again.",
}


def normalize_language(value: str | None) -> str | None:
    if not value:
        return None
    code = value.strip().lower().split("-", 1)[0]
    return code if code in SUPPORTED else None


def detect_language(cookie_value: str | None, accept_language: str | None) -> str:
    selected = normalize_language(cookie_value)
    if selected:
        return selected
    if not accept_language:
        return DEFAULT
    choices: list[tuple[float, str]] = []
    for part in accept_language.split(","):
        pieces = part.strip().split(";")
        tag = pieces[0].strip()
        quality = 1.0
        for piece in pieces[1:]:
            piece = piece.strip()
            if piece.startswith("q="):
                try:
                    quality = float(piece[2:])
                except ValueError:
                    quality = 0.0
        code = normalize_language(tag)
        if code:
            choices.append((quality, code))
    if not choices:
        return DEFAULT
    choices.sort(reverse=True)
    return choices[0][1]


def translate(lang: str, key: str, **kwargs: Any) -> str:
    table = SV if lang == "sv" else EN
    text = table.get(key)
    if text is None:
        text = key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def label(lang: str, group: str, code: str) -> str:
    return LABELS.get(lang, LABELS["en"]).get(group, {}).get(code, code)


def assurance(lang: str, code: str, mock: bool = False) -> str:
    text = label(lang, "assurance", code)
    if mock:
        text = f"{text} {MOCK.get(lang, MOCK['en'])}"
    return text


def payload(lang: str) -> dict[str, Any]:
    return {
        "lang": lang,
        "strings": SV if lang == "sv" else EN,
        "labels": LABELS.get(lang, LABELS["en"]),
    }


def cookie_header(config: Any, lang: str) -> str:
    parts = [
        f"{COOKIE_NAME}={lang}",
        "Path=/",
        "Max-Age=31536000",
        "SameSite=Lax",
        "HttpOnly",
    ]
    if getattr(config, "cookie_secure", False):
        parts.append("Secure")
    return "; ".join(parts)
