from PIL import Image
import os

def encontrar_faixa_padrao(imagem, cor_alvo, tolerancia_cor=15, altura_min=26, altura_max=32):
    """
    Encontra posições onde há o padrão vertical na coluna 325 com a cor especificada.
    Aceita variação de altura entre 26 e 32 pixels (29 ± 3).
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    coluna_x = 325  # Pixel específico a ser percorrido
    
    # Verifica se a imagem tem largura suficiente para acessar a coluna 325
    if largura <= coluna_x:
        print(f"Erro: A imagem tem largura de {largura}px, mas a coluna {coluna_x} foi solicitada.")
        return posicoes_corte

    y = 0
    while y < altura:
        # Conta quantos pixels consecutivos correspondem à cor alvo na coluna 325
        altura_contada = 0
        while y + altura_contada < altura:
            pixel = pixels[coluna_x, y + altura_contada]
            
            if len(pixel) == 4:  # RGBA
                r, g, b, _ = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se a cor está dentro da tolerância
            if (abs(r - cor_alvo[0]) <= tolerancia_cor and 
                abs(g - cor_alvo[1]) <= tolerancia_cor and 
                abs(b - cor_alvo[2]) <= tolerancia_cor):
                altura_contada += 1
            else:
                break

        # Se a altura contada estiver dentro da margem de erro (26 a 32 pixels)
        if altura_min <= altura_contada <= altura_max:
            # Corta 7 pixels antes de iniciar o padrão
            posicao_corte = max(0, y - 7)
            
            posicoes_corte.append(posicao_corte)
            print(f"Padrão encontrado em y={y} (altura: {altura_contada}px), cortando em y={posicao_corte}")
            
            # Avança o loop além da faixa detectada
            y += altura_contada
        else:
            y += max(1, altura_contada)  # Avança ao menos 1 pixel se não for o padrão
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando antes dos padrões encontrados.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_faixa_padrao(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} ocorrências do padrão para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Corta a seção final após o último ponto de corte
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "divididas"           # Substitua pelo nome da pasta de saída
    
    # Cor RGB (222, 221, 222) solicitada
    cor_do_padrao = (222, 221, 222)
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("Divisão concluída!")