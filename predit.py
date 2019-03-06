import os.path
import re
from functools import wraps

NO_LINK = r"(?!\[)\b{}\b(?!\])(?!\().*?(?!\))"
MACROS = []

BPO = "https://bugs.python.org/issue{}"
GHUB = "https://github.com/{}/{}"
PEPS = "https://www.python.org/dev/peps/pep-{}/"

def macro(pattern):
    def macro_helper(f):
        @wraps(f)
        def wrapper(match):
            return f(match)
                    
        f.pattern = re.compile(NO_LINK.format(pattern), re.MULTILINE | re.UNICODE )
        MACROS.append(f)
        return wrapper
    return macro_helper

@macro(r"PEP(\d{1,4})")
def pep_index(match):
    pep_number = match.group(1)
    return f"[PEP{pep_number}]({PEPS.format(pep_number.zfill(4))})"

@macro(r"bpo\-?(\d{1,5})")
def bpo(match):
    issue_number = match.group(1)
    return f"[bpo-{issue_number}]({BPO.format(issue_number)})"

@macro(r"g\/(\w+)\/(\w+)")
def github(match):
    repo, owner = match.group(1), match.group(2)
    return f"GH[{repo}/{owner}]({GHUB.format(repo, owner)})"

def main(files):
    if len(files) == 1 and os.path.isdir(files[0]):
        path = files[0]
        files = [f"{path}/{f}" for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.md')]
        print(files)
        
    for file in files:
        with open(file) as f:
            text = f.read()
            
        for macro in MACROS:
            text = re.sub(macro.pattern, macro, text)
        
        with open(file, 'w') as f:
            f.write(text)

def test():
    import textwrap
    text = textwrap.dedent(
        """
        g/python/cpython implementasyonunun standard kütüphanesi çoğunlukla PEP8'e
        uymaktadır fakat arada PEP282 ile gelen logging gibi kütüphaneler camelCase kullanarak problem
        yaratmaktadır. Backwards compability olayı yüzünden de kolayca değiştirilemiyor fakat belki
        Python4 ile beraber düzelir. Bazen de arada bpo13362'deki gibi katkıda bulunmak isteyenler çıkıyor
        bu mevzuya fakat rhettinger'ın da dediği gibi gerek yok bu kadar kasmaya.
        """
    )
    
    correct = textwrap.dedent(
        """
        GH[python/cpython](https://github.com/python/cpython) implementasyonunun standard kütüphanesi çoğunlukla [PEP8](https://www.python.org/dev/peps/pep-0008/)'e
        uymaktadır fakat arada [PEP282](https://www.python.org/dev/peps/pep-0282/) ile gelen logging gibi kütüphaneler camelCase kullanarak problem
        yaratmaktadır. Backwards compability olayı yüzünden de kolayca değiştirilemiyor fakat belki
        Python4 ile beraber düzelir. Bazen de arada [bpo-13362](https://bugs.python.org/issue13362)'deki gibi katkıda bulunmak isteyenler çıkıyor
        bu mevzuya fakat rhettinger'ın da dediği gibi gerek yok bu kadar kasmaya.
        """        
    )
    for macro in MACROS:
        text = re.sub(macro.pattern, macro, text)
    
    assert text == correct
    
if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
    

