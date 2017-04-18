"""Internationalization.

Use

  from i18n import translate as _

to enable string localization. In the future it would be easily
replaced by gettext since translatable strings are marked in the
same way as _("text").

Beside the translation service, this module defines the messages
used in the application, such as the help and the usage messages.
"""

import os
import atexit


############################################################
# Translation function
############################################################

def translate(text):
    """Translate the text in the current language."""
    try:
        return _strings[text]
    except KeyError:
        _missing_translation.add(text)
        s = (text if len (text) < 15 else text[:15] + "...")
        print("[TT] Warning: missing translation for '%s'" % s)
        return text


############################################################
# Application messages
############################################################
_strings = {}
_missing_translation = set()
_lang = 'en'

_it_strings = """
Run tests to verify the correctness of a program. $ Esegue dei test per verificare la correttezza di un programma.
set the verbosity level, where the level must be an integer between 0 (minimum) and 4 (maximum). The default value is 3. $ imposto il livello di verbosità.  Il livello deve essere un valore intero tra 0 (minimo) e 3 (massimo).  Il default è 2.
set how many seconds it should be waited for the termination of the program.  The default is 10 seconds. $ imposta per quanti secondi bisogna attendere la terminazione del programma.  Il default è pari a 10 secondi.
reports up to N errors per section (default 4). $ riporta fino ad un massimo di N errori per sezione (default 4).
uses the specified configuration file. $ utilizza il file di configurazione specificato.
enable or disable colored output (default AUTO). $ abilita o disabilita l'output colorato (default AUTO).
use Valgrind (if installed) to check memory usage. $ utilizza Valgrind (se installato) per controllare l'utilizzo della memoria.
select the output type. $ seleziona il tipo di output.
specify the name of the file used for logging.  The default is ~/.pvcheck.log. $ specifica il nome del file usato per il logging. Il default è ~/.pvcheck.log.
print this message and exit. $ stampa questo messaggio ed esce.
list all the available tests. $ mostra tutti i test disponibili.
run only the selected test. $ esegue solo il test indicato.
export in a file the input arguments from the selected test. $ salva in un file gli argomenti di input dal test indicato.
ERROR $ ERRORE
OK $ OK
WARNING! $ ATTENZIONE!
COMMAND LINE $ RIGA DI COMANDO
<temp.file> $ <file temp.>
INPUT $ INPUT
OUTPUT $ OUTPUT
TEMPORARY FILE $ FILE TEMPORANEO
TEST $ TEST
line %d $  riga %d
(expected '%s' $  (atteso '%s'
, got '%s')":  ottenuto '%s')
unexpected line '%s' $ riga inattesa '%s'
missing line (expected '%s') $ riga mancante (atteso '%s')
wrong number of lines (expected %d, got %d) $ numero di righe errato (atteso %d, ottenuto %d)
line %d is wrong  (expected '%s', got '%s') $ riga %d errata  (atteso '%s', ottenuto '%s')
The first %d lines matched correctly $ Le prime %d righe sono corrette
(... plus other %d errors ...) $ (... più altri %d errori ...)
ACTUAL OUTPUT $ OUTPUT EFFETTIVO
EXPECTED OUTPUT $ OUTPUT ATTESO
detailed comparison $ confronto dettagliato
<nothing> $ <niente>
missing section $ sezione mancante
empty section $ sezione vuota
extra section $ sezione extra
Invalid parameter ('%s') $ Parametro non valido ('%s')
Invalid parameter ('%d') $ Parametro non valido('%d')
"Invalid parameter ('%f') $ Parametro non valido('%f')
TIMEOUT EXPIRED: PROCESS TERMINATED $ TEMPO LIMITE SCADUTO: PROCESSO TERMINATO
PROCESS ENDED WITH A FAILURE $ PROCESSO TERMINATO CON UN FALLIMENTO
(SEGMENTATION FAULT) $ (SEGMENTATION FAULT)
(ERROR CODE {status}) $ (CODICE D'ERRORE {status})
FAILED TO RUN THE FILE '{progname}' $ IMPOSSIBILE ESEGUIRE IL FILE '{progname}'
(the file does not exist) $ (file inesistente)
(... plus other %d lines ...) $ (... più altre %d righe ...)
SUMMARY $ RIEPILOGO
successes $ successi
warnings $ avvertimenti
errors $ errori
<program> $ <programma>
CODE $ CODICE
TOTAL $ TOTALE
Test number %d doesn't exist. $ Il test numero %d non esiste.
Use 'list' to list all the available tests. $ Utilizza 'list' per vedere tutti i test disponibili.
Usage: list testfile $ Utilizzo: list fileditest
"Usage: N run[or export] testfile executable" $ Utilizzo: N run fileditest eseguibile
Error: Can't export test number %d. $ Errore: Impossibile esportare il test numero %d.
file containing the tests to be performed (default pvcheck.test). $ file contenente i test da eseguire (default pvcheck.test).
program to be tested. $ programma da testare.
any arguments of the program to be tested. $ eventuali argomenti del programma da testare.
"""

_translations = {
    'it': {
    }
}
_translations['it'].update(
    dict((a[0].strip(), a[2].strip()) for a in
         (b.partition('$') for b in _it_strings.splitlines())
         if len(a) == 3))


############################################################
# Setup and shutdown
############################################################

def _install_lang():
    global _lang
    global _strings
    _lang = os.environ.get('LANG', 'en').partition('_')[0]
    try:
        _strings = _translations[_lang]
    except KeyError:
        # Fallback to english, where the translation is the identity
        # function.
        _lang = 'en'
        for t in _translations.values():
            _strings = dict((k, k) for k in t)
            break

_install_lang()

@atexit.register
def _save_missing_translations():
    if _missing_translation:
        import pprint
        with open('missing_translations.txt', 'wt') as f:
            d = dict.fromkeys(_missing_translation, "")
            pprint.pprint({_lang:d}, stream=f)
