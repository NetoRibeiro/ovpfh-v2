#!/usr/bin/env python3
"""
Update Logo Paths
Updates HTML and JS files to use local logo paths instead of external URLs.
"""

import re
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent

# Logo mapping: external URL -> local path
LOGO_MAPPING = {
    # Teams
    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Flamengo-RJ_%28BRA%29.png/150px-Flamengo-RJ_%28BRA%29.png': 'assets/times/flamengo.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Palmeiras_logo.svg/150px-Palmeiras_logo.svg.png': 'assets/times/palmeiras.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Corinthians_simbolo.png/150px-Corinthians_simbolo.png': 'assets/times/corinthians.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Brasao_do_Sao_Paulo_Futebol_Clube.svg/150px-Brasao_do_Sao_Paulo_Futebol_Clube.svg.png': 'assets/times/sao-paulo.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Vasco_da_Gama.svg/150px-Vasco_da_Gama.svg.png': 'assets/times/vasco.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Santos_Logo.png/150px-Santos_Logo.png': 'assets/times/santos.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Botafogo_de_Futebol_e_Regatas_logo.svg/150px-Botafogo_de_Futebol_e_Regatas_logo.svg.png': 'assets/times/botafogo.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Fluminense_FC_escudo.png/150px-Fluminense_FC_escudo.png': 'assets/times/fluminense.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Atletico_mineiro_galo.png/150px-Atletico_mineiro_galo.png': 'assets/times/atletico-mg.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Cruzeiro_Esporte_Clube_%28logo%29.svg/150px-Cruzeiro_Esporte_Clube_%28logo%29.svg.png': 'assets/times/cruzeiro.png',
    
    # Leagues
    'https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Paulist%C3%A3o_logo.png/150px-Paulist%C3%A3o_logo.png': 'assets/campeonatos/paulistao.png',
    'https://upload.wikimedia.org/wikipedia/pt/thumb/e/e3/Campeonato_Carioca_logo.png/150px-Campeonato_Carioca_logo.png': 'assets/campeonatos/carioca.png',
    'https://upload.wikimedia.org/wikipedia/pt/thumb/4/4f/Campeonato_Mineiro_logo.png/150px-Campeonato_Mineiro_logo.png': 'assets/campeonatos/mineiro.png',
    
    # Channels
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Star%2B_logo_2021.svg/120px-Star%2B_logo_2021.svg.png': 'assets/canais/sportv.png',
}


def update_file(filepath, mapping):
    """
    Update a file by replacing external URLs with local paths.
    
    Args:
        filepath: Path to the file to update
        mapping: Dictionary of URL -> local path mappings
    
    Returns:
        int: Number of replacements made
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements = 0
        
        for external_url, local_path in mapping.items():
            if external_url in content:
                content = content.replace(external_url, local_path)
                replacements += content.count(local_path) - original_content.count(local_path)
        
        if replacements > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated {filepath.name}: {replacements} replacements")
        else:
            print(f"ℹ️  {filepath.name}: No changes needed")
        
        return replacements
        
    except Exception as e:
        print(f"❌ Error updating {filepath.name}: {e}")
        return 0


def update_all_files():
    """Update all HTML and JS files with local logo paths."""
    
    print("=" * 60)
    print("🔄 Updating logo paths to local files")
    print("=" * 60)
    print()
    
    files_to_update = [
        BASE_DIR / 'index.html',
        BASE_DIR / 'campeonatos.html',
        BASE_DIR / 'detalhes-do-jogo.html',
        BASE_DIR / 'app.js',
    ]
    
    total_replacements = 0
    
    for filepath in files_to_update:
        if filepath.exists():
            replacements = update_file(filepath, LOGO_MAPPING)
            total_replacements += replacements
        else:
            print(f"⚠️  File not found: {filepath.name}")
    
    print()
    print("=" * 60)
    print(f"✅ Complete! Made {total_replacements} total replacements")
    print("=" * 60)
    print()
    print("💡 Next step: Open index.html in your browser to verify")


if __name__ == "__main__":
    try:
        update_all_files()
    except KeyboardInterrupt:
        print("\n\n⚠️  Update interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
