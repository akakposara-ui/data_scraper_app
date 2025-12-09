import streamlit as st
import pandas as pd
from requests import get
from bs4 import BeautifulSoup as bs
from numpy import nan
import io
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3 
import config_style



# Thème de couleur personnalisé injecté via CSS dynamique
st.markdown(f"""
<style>
    /* 1. COULEURS DE FOND (Barre Latérale et Corps Principal) */
    
    /* Barre Latérale (Sidebar) */
    section[data-testid="stSidebar"] {{
        background-color: {config_style.BACKGROUND_SIDEBAR}; 
        border-right: 1px solid {config_style.ACCENT_COLOR_PRIMARY};
        transition: background-color 0.5s; /* Ajoute un effet visuel doux */
    }}
    
    /* Corps Principal (Main content) */
    .stApp {{
        background-color: {config_style.BACKGROUND_MAIN};
    }}

    /* 2. TYPOGRAPHIE ET ACCENTUATION */
    
    /* Titre principal (H1) */
    h1 {{
        color: {config_style.FONT_COLOR_HEADER}; 
        font-size: 2.5em;
        border-bottom: 2px solid {config_style.ACCENT_COLOR_PRIMARY}; 
        padding-bottom: 5px;
    }}
    
    /* Sous-titres (H3) */
    h3 {{
        color: {config_style.FONT_COLOR_SECONDARY};
        font-weight: 600;
        padding-top: 10px;
    }}
    
    /* Texte général */
    body, p, div, span, label {{
        color: {config_style.FONT_COLOR_PRIMARY};
    }}
    
    /* Améliorer les boutons (Download et Link) */
    .stDownloadButton button, .stLinkButton a, button {{
        background-color: {config_style.ACCENT_COLOR_PRIMARY}; 
        color: white !important;
        border-radius: 8px;
        transition: background-color 0.3s;
    }}
    
    /* Couleur au survol (Hover) */
    .stDownloadButton button:hover, .stLinkButton a:hover, button:hover {{
        background-color: {config_style.ACCENT_COLOR_SECONDARY};
        color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Ombre légère au survol */
    }}
</style>
""", unsafe_allow_html=True)

# Scraping about motos and scooters
def scrape_motos_scooters(num_pages):
    df_final = pd.DataFrame()
    base_url = 'https://dakar-auto.com/senegal/motos-and-scooters-3?&page='

    
    for i in range(1, num_pages + 1):
        url = f'{base_url}{i}'
        data = []

        try:
            res = get(url)
            soup = bs(res.content, 'html.parser')
            containers = soup.find_all('div', 'listing-card')

            
            for container in containers:
                dic = {} 
                try:
                    gen_inf_title = container.find('h2', 'listing-card__header__title mb-md-2 mb-0')
                    if gen_inf_title and gen_inf_title.a:
                        gen_inf = gen_inf_title.a.text.strip().split()
                        dic["brand"] = gen_inf[0] if len(gen_inf) > 0 else nan
                        dic["year"] = gen_inf[-1] if len(gen_inf) > 1 else nan

                    price_elem = container.find('h3', 'listing-card__header__price font-weight-bold text-uppercase mb-0')
                    if price_elem:
                        dic["price"] = "".join(price_elem.text.strip().split()).replace('FCFA', '')
                    else:
                        dic["price"] = nan

                    address_elem = container.find('div', 'col-12 entry-zone-address')
                    if address_elem:
                        dic["address"] = "".join("".join(address_elem.text).strip().split())
                    else:
                        dic["address"] = nan

                    gen_inf_list = container.find('ul', 'listing-card__attribute-list list-inline mb-0')
                    if gen_inf_list:
                        gen_inf_attrs = gen_inf_list.text.split()
                        dic["kilometerage"] = gen_inf_attrs[2] if len(gen_inf_attrs) > 2 else nan
                    else:
                        dic["kilometerage"] = nan
                            
                    owner_elem = container.find('p', 'time-author m-0')
                    if owner_elem:
                        dic["owner"] = owner_elem.text
                    else:
                        dic["owner"] = nan    

                    data.append(dic)

                except Exception as e:
                    print(f"Error: {e}")
                    pass 

            df_page = pd.DataFrame(data)
            df_final = pd.concat([df_final, df_page], ignore_index=True)

        except Exception as e:
            print(f"Error: {e}")
            continue 

    df_final = df_final.drop_duplicates().reset_index(drop=True)
    
    df_final['year'] = pd.to_numeric(df_final['year'], errors='coerce').astype('Int64')
    df_final['price'] = pd.to_numeric(df_final['price'], errors='coerce').astype('Int64')
    df_final['kilometerage'] = pd.to_numeric(df_final['kilometerage'], errors='coerce').astype('Int64')
    
    return df_final





# Scraping about car sale
def scrape_vente_voitures(num_pages):
    
    df_final2 = pd.DataFrame()
    base_url2 = 'https://dakar-auto.com/senegal/voitures-4?&page='

   
    for i in range(1, num_pages + 1):
        url = f'{base_url2}{i}'
        data2 = []

        try:
            res = get(url) 
            soup = bs(res.content, 'html.parser')
            containers = soup.find_all('div', 'listing-card')

            for container in containers:
                dic = {} 
                try:
                    gen_inf_title = container.find('h2', 'listing-card__header__title mb-md-2 mb-0')
                    if gen_inf_title and gen_inf_title.a:
                        gen_inf = gen_inf_title.a.text.strip().split()
                        dic["brand"] = gen_inf[0] if len(gen_inf) > 0 else nan
                        dic["year"] = gen_inf[-1] if len(gen_inf) > 1 else nan

                    price_elem = container.find('h3', 'listing-card__header__price font-weight-bold text-uppercase mb-0')
                    if price_elem:
                        dic["price"] = "".join(price_elem.text.strip().split()).replace('FCFA', '')
                    else:
                        dic["price"] = nan

                    address_elem = container.find('div', 'col-12 entry-zone-address')
                    if address_elem:
                        dic["address"] = "".join("".join(address_elem.text).strip().split())
                    else:
                        dic["address"] = nan

                    gen_inf_list = container.find('ul', 'listing-card__attribute-list list-inline mb-0')
                    if gen_inf_list:
                        gen_inf_attrs = gen_inf_list.text.split()
                        dic["kilometerage"] = gen_inf_attrs[2] if len(gen_inf_attrs) > 2 else nan
                    else:
                        dic["kilometerage"] = nan
                        
                    gen_inf_list2 = container.find('ul', 'listing-card__attribute-list list-inline mb-0')
                    if gen_inf_list2:
                        gen_inf_attrs2 = gen_inf_list2.text.split()
                        dic["gearbox"] = gen_inf_attrs2[4] if len(gen_inf_attrs2) > 4 else nan
                    else:
                        dic["gearbox"] = nan    
                        
                      
                    gen_inf_list3 = container.find('ul', 'listing-card__attribute-list list-inline mb-0')
                    if gen_inf_list3:
                        gen_inf_attrs3 = gen_inf_list3.text.split()
                        dic["fuel"] = gen_inf_attrs3[5] if len(gen_inf_attrs3) > 5 else nan
                    else:
                        dic["fuel"] = nan   
                        
                    owner_elem = container.find('p', 'time-author m-0')
                    if owner_elem:
                        dic["owner"] = owner_elem.text.replace("Par ", " ")
                    else:
                        dic["owner"] = nan    

                    data2.append(dic)

                except Exception as e:
                    print(f"Error: {e}")
                    pass 

            df_page = pd.DataFrame(data2)
            df_final2 = pd.concat([df_final2, df_page], ignore_index=True)

        except Exception as e:
            print(f"Error: {e}")
            continue 

    df_final2 = df_final2.drop_duplicates().reset_index(drop=True)
    
    df_final2['year'] = pd.to_numeric(df_final2['year'], errors='coerce').astype('Int64')
    df_final2['price'] = pd.to_numeric(df_final2['price'], errors='coerce').astype('Int64')
    df_final2['kilometerage'] = pd.to_numeric(df_final2['kilometerage'], errors='coerce').astype('Int64')
    
    return df_final2



# Scraping about cars location
def scrape_location_voitures(num_pages):
    
    df_final3 = pd.DataFrame()
    base_url3 = 'https://dakar-auto.com/senegal/location-de-voitures-19?&page='

   
    for i in range(1, num_pages + 1):
        url = f'{base_url3}{i}'
        data3 = []

        try:
            res = get(url)
            soup = bs(res.content, 'html.parser')
            containers = soup.find_all('div', 'listing-card__content__inner')

            for container in containers:
                dic = {} 
                try:
                    gen_inf_title = container.find('h2', 'listing-card__header__title mb-md-2 mb-0')
                    if gen_inf_title and gen_inf_title.a:
                        gen_inf = gen_inf_title.a.text.strip().split()
                        dic["brand"] = gen_inf[0] if len(gen_inf) > 0 else nan
                        dic["year"] = gen_inf[-1] if len(gen_inf) > 1 else nan

                    price_elem = container.find('h3', 'listing-card__header__price font-weight-bold text-uppercase mb-0')
                    if price_elem:
                        dic["price"] = "".join(price_elem.text.strip().split()).replace('FCFA', '')
                    else:
                        dic["price"] = nan
                        
                    address_elem = container.find('div', 'col-12 entry-zone-address')
                    if address_elem:
                        dic["address"] = "".join("".join(address_elem.text).strip().split())
                    else:
                        dic["address"] = nan
                        
                    owner_elem = container.find('p', 'time-author m-0')
                    if owner_elem:
                        dic["owner"] = owner_elem.text.replace("Par ", " ")
                    else:
                        dic["owner"] = nan    

                    data3.append(dic)

                except Exception as e:
                    print(f"Error: {e}")
                    pass 

            df_page = pd.DataFrame(data3)
            df_final3 = pd.concat([df_final3, df_page], ignore_index=True)

        except Exception as e:
            print(f"Error: {e}")
            continue 

    df_final3['year'] = pd.to_numeric(df_final3['year'], errors='coerce').astype('Int64')
    df_final3['price'] = pd.to_numeric(df_final3['price'], errors='coerce').astype('Int64')
    return df_final3






##################################################################################


DB_FILE = 'my_app.db'


def clean_dataframe(df) :
    if 'brand' in df.columns:
        df['brand'] = df['brand'].astype(str).str.split().str[0]
        
    if 'price' in df.columns:
        df['price'] = df['price'].astype(str).str.replace(r'[^\d]', '', regex=True)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').astype('Int64')
        
    if 'year' in df.columns:
        df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')

    if 'kilometerage' in df.columns:
        df['kilometerage'] = df['kilometerage'].astype(str).str.replace(r'[^\d]', '', regex=True)
        df['kilometerage'] = pd.to_numeric(df['kilometerage'], errors='coerce').astype('Int64')
        
    if 'owner' in df.columns:
        df['owner'] = df['owner'].astype(str).str.replace(r'[\r\n]', '', regex=True).str.strip().str.replace('Par ', '').str.strip()

    return df

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


@st.cache_data(show_spinner="Loading data from database...")
def load_data_from_db(table_name):
    try:
        with sqlite3.connect(DB_FILE) as conn: 
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        return clean_dataframe(df)

    except sqlite3.OperationalError as e:
        st.error(f"The table '{table_name}'do not exist. ({e})")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error during to load data from {table_name}: {e}")
        return pd.DataFrame()


def display_data_table(df, title):
    st.subheader(title)
    st.dataframe(df)

    csv = convert_df_to_csv(df)
    st.download_button(
        label="Download data in CSV",
        data=csv,
        file_name=f'{title.replace(" ", "_").replace("(", "").replace(")", "").replace(" ", "")}_data.csv',
        mime='text/csv',
    )
    st.markdown("---")


def display_dashboard(table_name, title): 
    st.title(f"Dasboard : {title}")
    
    df = load_data_from_db(table_name)

    if df.empty:
        return

    st.success(f"Loading data from **{table_name}** ({len(df)} lignes)")
    
    if 'price' in df.columns and 'gearbox' in df.columns and not df['gearbox'].isnull().all():
        st.subheader("Price distribution per gearbox")
        fig, ax = plt.subplots()
        sns.boxplot(x='gearbox', y='price', data=df, ax=ax)
        ax.set_title("Boxplot du Prix par Boîte de Vitesse")
        st.pyplot(fig)
        

    st.subheader(f"Top 10 of brand in {title}")
    brand_counts = df['brand'].value_counts().nlargest(10)
    st.bar_chart(brand_counts)

    if 'year' in df.columns and not df['year'].isnull().all():
        st.subheader("Year tendancy of cars")
        year_counts = df['year'].value_counts().sort_index()
        st.bar_chart(year_counts)


def main():
    st.set_page_config(layout="wide", page_title="Data Scraper")
    
    DB_TABLES = {
        'Motors and scooters for sales': 'moto_Scooters_cleaned',
        'Cars for location': 'location_car_cleaned',
        'Cars for sale': 'car_sale_cleaned'
    }
    TITLE_MAP = {
        'Motors and scooters for sales': 'Motos and Scooters for sale',
        'Cars for location': 'Cars for location',
        'Cars for sale': 'Cars for sale'
    }
    
    # (SIDEBAR/MENU)
    with st.sidebar:
        
        st.header("Available sites")
        site_options = {
            'Motors and scooters for sale': {'func': scrape_motos_scooters, 'max_pages': 55},
            'Cars for location': {'func': scrape_location_voitures, 'max_pages': 9},
            'Cars for sale': {'func': scrape_vente_voitures, 'max_pages': 200}
        }
        selected_site = st.selectbox("Select your category option:", list(site_options.keys()), key='selected_site')
        site_info = site_options[selected_site]
        max_pages = site_info['max_pages']
        st.markdown("---")

        st.header("Numbers of pages")
        num_pages = st.slider(f"Number of pages (1 to {max_pages} max) :", min_value=1, max_value=max_pages, value=min(3, max_pages), key='num_pages')
        if st.button("Validate & Launch Scraping"):
            st.session_state['scraping_triggered'] = True
            st.session_state['site'] = selected_site
            st.session_state['pages'] = num_pages
        st.markdown("---")
        
        st.header("View dashboard of available data")
        st.session_state['dashboard_select'] = st.selectbox(
            "Visualize existant data:",
            ['Select one category', 'Motors and scooters for sales', 'Cars for location', 'Cars for sale'],
            key='dashboard_select_menu'
        )
        st.markdown("---")
        
        st.header("Evaluate the application")
        if st.button('Forms'):
            st.session_state['show_evaluation'] = True
        else:
            if 'show_evaluation' not in st.session_state: st.session_state['show_evaluation'] = False


    # --- PARTIE DROITE (PRINCIPAL) ---
    st.title("Data Scraper")
    st.markdown("This application aims to help you scrape data from the mentioned category and view existing data dashboards.")
    st.markdown("---")
    
    feedback_placeholder = st.empty()


    dashboard_choice = st.session_state.get('dashboard_select')
    if dashboard_choice in DB_TABLES:
        table_name = DB_TABLES[dashboard_choice]
        display_dashboard(table_name, TITLE_MAP[dashboard_choice])
        
    if st.session_state.get('scraping_triggered', False) and 'site' in st.session_state:
        site = st.session_state['site']
        pages = st.session_state['pages']
        st.session_state['scraping_triggered'] = False 

        st.header(f"Result of scraping : {site}")
        site_func = site_options[site]['func']
        
        with feedback_placeholder.container():
            df_scraped = site_func(pages)
            
        
        if not df_scraped.empty:
            display_data_table(df_scraped, f"Scraped data about {site}")
        else:
            st.warning("No result")

    # Affichage de tables existantes
    st.header("Let look at a quick visualization of our available data")
    
    data_tables_quick_view = {
        "Motors and Scooters": ('moto_Scooters_cleaned', "Motos and Scooters"),
        "Cars for location": ('location_car_cleaned', "Cars for location"),
        "Cars for sale": ('car_sale_cleaned', "Cars for sale"),
    }
    
    cols = st.columns(3)
    for i, (label, (table_name, title)) in enumerate(data_tables_quick_view.items()):
        if cols[i].button(label):
            df_existing = load_data_from_db(table_name)
            
            if not df_existing.empty:
                display_data_table(df_existing, title)
            else:
                st.warning(f"The table **{table_name}** is empty or unavailable.")
    st.markdown("---")
    
    # App evaluation
    if st.session_state.get('show_evaluation'):
        st.header("Evaluate the application")
        st.markdown("Your evaluation is important to upgrade the app, so don't be lazy to do it!!")
        
        kobo_link = "https://ee.kobotoolbox.org/single/E5s8cx29"
        google_link = "https://docs.google.com/forms/d/e/1FAIpQLSdoapTNo7JxPP3dbdqdPmdf-AnjfS89pGixt4lyriWVce5Prw/viewform?usp=header"

        col_kobo, col_google = st.columns(2)
        
        with col_kobo:
            st.link_button("KoboToolBox form", kobo_link)
        
        with col_google:
            st.link_button("Google Form", google_link)


if __name__ == "__main__":
    main()
