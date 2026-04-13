import streamlit as st
import requests
from datetime import datetime
import json

# ==================== CONFIGURAÇÕES (usando secrets) ====================
# As chaves são lidas do Streamlit Cloud Secrets (ou .streamlit/secrets.toml local)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Configuração da página
st.set_page_config(
    page_title="DM Dance School - Admin",
    page_icon="🩰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== FUNÇÕES AUXILIARES ====================
def upload_para_storage(arquivo, pasta="banners"):
    """Faz upload da imagem para o Supabase Storage"""
    try:
        import requests as req
        
        file_content = arquivo.read()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"{timestamp}_{arquivo.name.replace(' ', '_')}"
        
        storage_url = f"{SUPABASE_URL}/storage/v1/object/{pasta}/{file_name}"
        
        storage_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": arquivo.type
        }
        
        response = req.post(storage_url, headers=storage_headers, data=file_content)
        
        if response.status_code in [200, 201]:
            return f"{SUPABASE_URL}/storage/v1/object/public/{pasta}/{file_name}"
        else:
            st.error(f"Erro no upload: {response.text}")
            return None
    except Exception as e:
        st.error(f"Erro: {e}")
        return None

def listar_registos(tabela):
    """Lista registos de uma tabela"""
    response = requests.get(f"{SUPABASE_URL}/rest/v1/{tabela}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def eliminar_registo(tabela, id_registo):
    """Elimina um registo"""
    response = requests.delete(f"{SUPABASE_URL}/rest/v1/{tabela}?id=eq.{id_registo}", headers=headers)
    return response.status_code == 204

# ==================== INTERFACE ====================
st.title("🩰 DM Dance School")
st.subheader("Painel Administrativo - Conteúdos")

# Menu lateral
menu = st.sidebar.radio(
    "📋 MENU PRINCIPAL",
    [
        "🏠 Dashboard",
        "📢 Comunicados",
        "🎵 Coreografias",
        "📸 Galeria de Fotos",
        "🎲 Fotos do Banner (Login)",
        "💬 Frases Inspiracionais",
        "🕰️ Horários",
        "📅 Próximos Eventos",
        "🎨 Banner do Dia",
        "📊 Ver Todos os Dados"
    ]
)

# ==================== DASHBOARD ====================
if menu == "🏠 Dashboard":
    st.header("🏠 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Contagens
    for tabela, nome, cor in [
        ("comunicados", "Comunicados", "📢"),
        ("coreografias", "Coreografias", "🎵"),
        ("galeria", "Fotos", "📸"),
        ("eventos", "Eventos", "📅")
    ]:
        dados = listar_registos(tabela)
        with eval(f"col{['1','2','3','4'][['comunicados','coreografias','galeria','eventos'].index(tabela)]}"):
            st.metric(nome, len(dados), delta=None)
            st.caption(f"{cor} Total de {nome.lower()}")
    
    st.divider()
    
    # Últimos comunicados
    st.subheader("📢 Últimos Comunicados")
    comunicados = listar_registos("comunicados")
    if comunicados:
        for item in comunicados[:3]:
            with st.container(border=True):
                st.write(f"**{item['titulo']}** - {item.get('data', 'Sem data')}")
                st.write(item['mensagem'][:100] + "..." if len(item['mensagem']) > 100 else item['mensagem'])
    else:
        st.info("Nenhum comunicado ainda")
    
    # Próximos eventos
    st.subheader("📅 Próximos Eventos")
    eventos = listar_registos("eventos")
    if eventos:
        for item in eventos[:3]:
            with st.container(border=True):
                st.write(f"**{item['titulo']}** - {item.get('data_evento', 'Sem data')}")
                st.write(item.get('local', 'Local não definido'))
    else:
        st.info("Nenhum evento agendado")

# ==================== COMUNICADOS ====================
elif menu == "📢 Comunicados":
    st.header("📢 Gestão de Comunicados")
    
    # Formulário para novo comunicado
    with st.expander("➕ Adicionar novo comunicado", expanded=True):
        with st.form("form_comunicado"):
            titulo = st.text_input("Título *")
            mensagem = st.text_area("Mensagem *", height=150)
            data = st.date_input("Data", datetime.now())
            destaque = st.checkbox("Destacar (banner na app)")
            
            if st.form_submit_button("Publicar Comunicado"):
                if titulo and mensagem:
                    novo = {
                        "titulo": titulo,
                        "mensagem": mensagem,
                        "data": data.strftime("%d/%m/%Y"),
                        "destaque": destaque,
                        "created_at": datetime.now().isoformat()
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/comunicados", headers=headers, json=novo)
                    if response.status_code == 201:
                        st.success("✅ Comunicado publicado com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"Erro: {response.text}")
                else:
                    st.warning("Preencha o título e a mensagem")
    
    # Listar comunicados existentes
    st.subheader("📋 Comunicados existentes")
    comunicados = listar_registos("comunicados")
    
    if comunicados:
        for item in comunicados:
            with st.expander(f"📢 {item['titulo']} - {item.get('data', 'Sem data')}"):
                st.write(item['mensagem'])
                st.caption(f"ID: {item['id']} | Criado: {item.get('created_at', 'N/A')[:10]}")
                if st.button(f"🗑️ Eliminar", key=f"del_com_{item['id']}"):
                    if eliminar_registo("comunicados", item['id']):
                        st.success("✅ Comunicado eliminado!")
                        st.rerun()
                    else:
                        st.error("Erro ao eliminar")
    else:
        st.info("Nenhum comunicado publicado ainda")

# ==================== COREOGRAFIAS ====================
elif menu == "🎵 Coreografias":
    st.header("🎵 Gestão de Coreografias")
    
    # Buscar modalidades existentes dos alunos
    response = requests.get(f"{SUPABASE_URL}/rest/v1/alunos?select=modalidade1,modalidade2,modalidade3,modalidade4", headers=headers)
    modalidades_set = set()
    if response.status_code == 200:
        for aluno in response.json():
            for m in ['modalidade1', 'modalidade2', 'modalidade3', 'modalidade4']:
                if aluno.get(m) and aluno.get(m) not in ['', None]:
                    modalidades_set.add(aluno[m])
    modalidades_lista = sorted(list(modalidades_set))
    
    with st.expander("➕ Adicionar coreografia", expanded=True):
        with st.form("form_coreografia"):
            titulo = st.text_input("Título da Coreografia *")
            modalidade = st.selectbox("Modalidade *", [""] + modalidades_lista)
            video_url = st.text_input("Link do YouTube/Vimeo")
            musica = st.text_input("Nome da Música")
            
            if st.form_submit_button("Adicionar Coreografia"):
                if titulo and modalidade:
                    nova = {
                        "titulo": titulo,
                        "modalidade": modalidade,
                        "video_url": video_url,
                        "musica": musica,
                        "created_at": datetime.now().isoformat()
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/coreografias", headers=headers, json=nova)
                    if response.status_code == 201:
                        st.success("✅ Coreografia adicionada!")
                        st.rerun()
                    else:
                        st.error(f"Erro: {response.text}")
                else:
                    st.warning("Preencha o título e a modalidade")
    
    st.subheader("📋 Coreografias existentes")
    coreografias = listar_registos("coreografias")
    
    if coreografias:
        for item in coreografias:
            with st.expander(f"🎵 {item['titulo']} - {item['modalidade']}"):
                st.write(f"🎶 **Música:** {item.get('musica', 'Não definida')}")
                if item.get('video_url'):
                    st.write(f"📺 **Link:** {item['video_url']}")
                if st.button(f"🗑️ Eliminar", key=f"del_coreo_{item['id']}"):
                    if eliminar_registo("coreografias", item['id']):
                        st.success("✅ Coreografia eliminada!")
                        st.rerun()
    else:
        st.info("Nenhuma coreografia adicionada ainda")

# ==================== GALERIA DE FOTOS ====================
elif menu == "📸 Galeria de Fotos":
    st.header("📸 Gestão da Galeria de Fotos")
    
    with st.expander("➕ Adicionar foto", expanded=True):
        with st.form("form_foto"):
            evento = st.text_input("Nome do Evento *")
            legenda = st.text_input("Legenda da foto")
            uploaded_file = st.file_uploader("Escolher foto", type=["jpg", "jpeg", "png"])
            
            if st.form_submit_button("Adicionar Foto"):
                if evento and uploaded_file:
                    foto_url = upload_para_storage(uploaded_file, "galeria")
                    if foto_url:
                        nova = {
                            "evento": evento,
                            "legenda": legenda,
                            "foto_url": foto_url,
                            "data_evento": datetime.now().strftime("%d/%m/%Y"),
                            "created_at": datetime.now().isoformat()
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/galeria", headers=headers, json=nova)
                        if response.status_code == 201:
                            st.success("✅ Foto adicionada à galeria!")
                            st.rerun()
                        else:
                            st.error(f"Erro: {response.text}")
                else:
                    st.warning("Preencha o evento e selecione uma foto")
    
    st.subheader("📋 Fotos na galeria")
    fotos = listar_registos("galeria")
    
    if fotos:
        cols = st.columns(3)
        for i, item in enumerate(fotos):
            with cols[i % 3]:
                try:
                    st.image(item['foto_url'], use_container_width=True)
                    st.caption(f"**{item['evento']}**")
                    st.caption(item['legenda'] if item['legenda'] else "")
                    if st.button(f"🗑️", key=f"del_foto_{item['id']}"):
                        if eliminar_registo("galeria", item['id']):
                            st.rerun()
                except:
                    st.warning("Imagem não disponível")
    else:
        st.info("Nenhuma foto na galeria ainda")

# ==================== FOTOS DO BANNER ====================
elif menu == "🎲 Fotos do Banner (Login)":
    st.header("🎲 Fotos para o Banner do Login")
    st.caption("Estas fotos aparecerão aleatoriamente no ecrã inicial da app dos pais")
    
    with st.expander("➕ Adicionar foto ao banner", expanded=True):
        with st.form("form_banner"):
            legenda = st.text_input("Legenda (opcional)")
            uploaded_file = st.file_uploader("Escolher foto", type=["jpg", "jpeg", "png"], key="banner_upload")
            
            if st.form_submit_button("Adicionar ao Banner"):
                if uploaded_file:
                    foto_url = upload_para_storage(uploaded_file, "banners")
                    if foto_url:
                        nova = {
                            "legenda": legenda,
                            "foto_url": foto_url,
                            "ativo": True,
                            "created_at": datetime.now().isoformat()
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/banner_fotos", headers=headers, json=nova)
                        if response.status_code == 201:
                            st.success("✅ Foto adicionada ao banner!")
                            st.rerun()
                        else:
                            st.error(f"Erro: {response.text}")
                else:
                    st.warning("Selecione uma foto")
    
    st.subheader("📋 Fotos do Banner")
    banners = listar_registos("banner_fotos")
    
    if banners:
        for item in banners:
            col1, col2 = st.columns([3, 1])
            with col1:
                try:
                    st.image(item['foto_url'], width=200, caption=item['legenda'] if item['legenda'] else "")
                except:
                    st.warning("Imagem não disponível")
            with col2:
                if st.button(f"🗑️ Eliminar", key=f"del_banner_{item['id']}"):
                    if eliminar_registo("banner_fotos", item['id']):
                        st.rerun()
    else:
        st.info("Nenhuma foto no banner ainda")

# ==================== FRASES INSPIRACIONAIS ====================
elif menu == "💬 Frases Inspiracionais":
    st.header("💬 Frases Inspiracionais")
    st.caption("Frases de dança que aparecerão aleatoriamente na app")
    
    with st.expander("➕ Adicionar frase", expanded=True):
        with st.form("form_frase"):
            frase = st.text_area("Frase *", height=80)
            autor = st.text_input("Autor (ex: Martha Graham)")
            
            if st.form_submit_button("Adicionar Frase"):
                if frase:
                    nova = {
                        "frase": frase,
                        "autor": autor if autor else None,
                        "ativo": True,
                        "created_at": datetime.now().isoformat()
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/frases", headers=headers, json=nova)
                    if response.status_code == 201:
                        st.success("✅ Frase adicionada!")
                        st.rerun()
                    else:
                        st.error(f"Erro: {response.text}")
                else:
                    st.warning("Escreva a frase")
    
    st.subheader("📋 Frases existentes")
    frases = listar_registos("frases")
    
    if frases:
        for item in frases:
            with st.expander(f"💬 \"{item['frase'][:60]}...\""):
                st.write(f"**Frase completa:** {item['frase']}")
                if item.get('autor'):
                    st.write(f"**Autor:** {item['autor']}")
                st.caption(f"ID: {item['id']}")
                if st.button(f"🗑️ Eliminar", key=f"del_frase_{item['id']}"):
                    if eliminar_registo("frases", item['id']):
                        st.rerun()
    else:
        st.info("Nenhuma frase adicionada ainda")

# ==================== HORÁRIOS ====================
elif menu == "🕰️ Horários":
    st.header("🕰️ Gestão de Horários")
    
    dias_semana = {
        0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira",
        3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
    }
    
    # Buscar modalidades
    response = requests.get(f"{SUPABASE_URL}/rest/v1/alunos?select=modalidade1,modalidade2,modalidade3,modalidade4", headers=headers)
    modalidades_set = set()
    if response.status_code == 200:
        for aluno in response.json():
            for m in ['modalidade1', 'modalidade2', 'modalidade3', 'modalidade4']:
                if aluno.get(m) and aluno.get(m) not in ['', None]:
                    modalidades_set.add(aluno[m])
    modalidades_lista = sorted(list(modalidades_set))
    
    with st.expander("➕ Adicionar horário", expanded=True):
        with st.form("form_horario"):
            modalidade = st.selectbox("Modalidade *", [""] + modalidades_lista)
            dia = st.selectbox("Dia da semana *", list(dias_semana.items()), format_func=lambda x: x[1])
            hora_inicio = st.time_input("Hora de início *")
            hora_fim = st.time_input("Hora de fim *")
            sala = st.text_input("Sala")
            professor = st.text_input("Professor")
            
            if st.form_submit_button("Adicionar Horário"):
                if modalidade and dia and hora_inicio and hora_fim:
                    novo = {
                        "modalidade": modalidade,
                        "dia_semana": dia[0],
                        "hora_inicio": hora_inicio.strftime("%H:%M"),
                        "hora_fim": hora_fim.strftime("%H:%M"),
                        "sala": sala if sala else None,
                        "professor": professor if professor else None,
                        "created_at": datetime.now().isoformat()
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/horarios", headers=headers, json=novo)
                    if response.status_code == 201:
                        st.success("✅ Horário adicionado!")
                        st.rerun()
                    else:
                        st.error(f"Erro: {response.text}")
                else:
                    st.warning("Preencha os campos obrigatórios")
    
    st.subheader("📋 Horários existentes")
    horarios = listar_registos("horarios")
    
    if horarios:
        for item in horarios:
            with st.expander(f"🕰️ {item['modalidade']} - {dias_semana.get(item['dia_semana'], '?')} às {item['hora_inicio']}"):
                st.write(f"**Horário:** {item['hora_inicio']} - {item['hora_fim']}")
                st.write(f"**Sala:** {item.get('sala', 'Não definida')}")
                st.write(f"**Professor:** {item.get('professor', 'Não definido')}")
                if st.button(f"🗑️ Eliminar", key=f"del_horario_{item['id']}"):
                    if eliminar_registo("horarios", item['id']):
                        st.rerun()
    else:
        st.info("Nenhum horário adicionado ainda")

# ==================== PRÓXIMOS EVENTOS ====================
elif menu == "📅 Próximos Eventos":
    st.header("📅 Gestão de Próximos Eventos")
    
    with st.expander("➕ Adicionar evento", expanded=True):
        with st.form("form_evento"):
            titulo = st.text_input("Título do Evento *")
            data_evento = st.date_input("Data do Evento", datetime.now())
            local = st.text_input("Local")
            preco = st.text_input("Preço (ex: 10€, Gratuito)")
            descricao = st.text_area("Descrição")
            
            if st.form_submit_button("Adicionar Evento"):
                if titulo:
                    novo = {
                        "titulo": titulo,
                        "data_evento": data_evento.strftime("%d/%m/%Y"),
                        "local": local if local else None,
                        "preco": preco if preco else None,
                        "descricao": descricao if descricao else None,
                        "created_at": datetime.now().isoformat()
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/eventos", headers=headers, json=novo)
                    if response.status_code == 201:
                        st.success("✅ Evento adicionado!")
                        st.rerun()
                    else:
                        st.error(f"Erro: {response.text}")
                else:
                    st.warning("Preencha o título")
    
    st.subheader("📋 Próximos Eventos")
    eventos = listar_registos("eventos")
    
    if eventos:
        for item in eventos:
            with st.expander(f"📅 {item['titulo']} - {item.get('data_evento', 'Sem data')}"):
                st.write(f"📍 **Local:** {item.get('local', 'Não definido')}")
                st.write(f"💰 **Preço:** {item.get('preco', 'Não definido')}")
                st.write(f"📝 **Descrição:** {item.get('descricao', 'Sem descrição')}")
                if st.button(f"🗑️ Eliminar", key=f"del_evento_{item['id']}"):
                    if eliminar_registo("eventos", item['id']):
                        st.rerun()
    else:
        st.info("Nenhum evento agendado")

# ==================== BANNER DO DIA ====================
elif menu == "🎨 Banner do Dia":
    st.header("🎨 Banner do Dia (Foto + Frase)")
    st.caption("Configure a foto e frase que aparecerão hoje no ecrã de login")
    
    # Buscar fotos disponíveis
    fotos = listar_registos("banner_fotos")
    frases = listar_registos("frases")
    
    if not fotos:
        st.warning("⚠️ Adicione fotos ao banner primeiro!")
    if not frases:
        st.warning("⚠️ Adicione frases inspiracionais primeiro!")
    
    with st.form("form_banner_dia"):
        foto_opcoes = {f"{item.get('legenda', item['id'])}": item['id'] for item in fotos}
        frase_opcoes = {f"{item['frase'][:50]}...": item['id'] for item in frases}
        
        foto_selecionada = st.selectbox("Foto do dia", list(foto_opcoes.keys())) if fotos else None
        frase_selecionada = st.selectbox("Frase do dia", list(frase_opcoes.keys())) if frases else None
        data_inicio = st.date_input("Data de início", datetime.now())
        data_fim = st.date_input("Data de fim (opcional)", value=None)
        
        if st.form_submit_button("Definir Banner do Dia"):
            if foto_selecionada and frase_selecionada:
                foto_id = foto_opcoes[foto_selecionada]
                foto_url = next((f['foto_url'] for f in fotos if f['id'] == foto_id), None)
                frase_id = frase_opcoes[frase_selecionada]
                
                novo = {
                    "foto_url": foto_url,
                    "frase_id": frase_id,
                    "data_inicio": data_inicio.strftime("%Y-%m-%d"),
                    "data_fim": data_fim.strftime("%Y-%m-%d") if data_fim else None,
                    "ativo": True,
                    "created_at": datetime.now().isoformat()
                }
                response = requests.post(f"{SUPABASE_URL}/rest/v1/banner_dia", headers=headers, json=novo)
                if response.status_code == 201:
                    st.success("✅ Banner do dia configurado!")
                    st.rerun()
                else:
                    st.error(f"Erro: {response.text}")
    
    # Mostrar banner atual
    st.subheader("📋 Banner atual")
    banners_dia = listar_registos("banner_dia")
    if banners_dia:
        ultimo = banners_dia[-1]
        col1, col2 = st.columns(2)
        with col1:
            try:
                st.image(ultimo['foto_url'], use_container_width=True)
            except:
                st.warning("Imagem não disponível")
        with col2:
            frase = next((f for f in frases if f['id'] == ultimo['frase_id']), None)
            if frase:
                st.write(f"💬 \"{frase['frase']}\"")
                if frase.get('autor'):
                    st.caption(f"— {frase['autor']}")
    else:
        st.info("Nenhum banner do dia configurado")

# ==================== VER TODOS OS DADOS ====================
elif menu == "📊 Ver Todos os Dados":
    st.header("📊 Dados no Supabase")
    
    abas = st.tabs(["Comunicados", "Coreografias", "Galeria", "Banner Fotos", "Frases", "Horários", "Eventos", "Banner Dia"])
    
    tabelas = ["comunicados", "coreografias", "galeria", "banner_fotos", "frases", "horarios", "eventos", "banner_dia"]
    
    for i, (tab, tabela) in enumerate(zip(abas, tabelas)):
        with tab:
            dados = listar_registos(tabela)
            if dados:
                st.json(dados)
            else:
                st.info(f"Nenhum dado na tabela {tabela}")

# ==================== RODAPÉ ====================
st.sidebar.divider()
st.sidebar.caption("🩰 DM Dance School - Painel Administrativo")
st.sidebar.caption(f"Versão 1.0 | {datetime.now().strftime('%Y')}")