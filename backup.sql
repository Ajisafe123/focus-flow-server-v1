--
-- PostgreSQL database dump
--

\restrict flJXfROPitwcx6X9Crwqageuj7GdPE5f0UUaUv4gSfIGTBWH9tw1JkWQv3oyV4I

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_notes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admin_notes (
    id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    admin_id uuid NOT NULL,
    note_text text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.admin_notes OWNER TO postgres;

--
-- Name: admin_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admin_users (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    is_online boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.admin_users OWNER TO postgres;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: allah_names; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.allah_names (
    id integer NOT NULL,
    arabic character varying,
    transliteration character varying,
    meaning character varying
);


ALTER TABLE public.allah_names OWNER TO postgres;

--
-- Name: allah_names_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.allah_names_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.allah_names_id_seq OWNER TO postgres;

--
-- Name: allah_names_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.allah_names_id_seq OWNED BY public.allah_names.id;


--
-- Name: bookmarks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bookmarks (
    id integer NOT NULL,
    user_id uuid,
    ayah_key character varying
);


ALTER TABLE public.bookmarks OWNER TO postgres;

--
-- Name: bookmarks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bookmarks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bookmarks_id_seq OWNER TO postgres;

--
-- Name: bookmarks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bookmarks_id_seq OWNED BY public.bookmarks.id;


--
-- Name: chat_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_users (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    avatar_letter character varying(1),
    created_at timestamp without time zone,
    last_seen timestamp without time zone,
    is_online boolean
);


ALTER TABLE public.chat_users OWNER TO postgres;

--
-- Name: contact_messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contact_messages (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    subject character varying(150) NOT NULL,
    message text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.contact_messages OWNER TO postgres;

--
-- Name: contact_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contact_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contact_messages_id_seq OWNER TO postgres;

--
-- Name: contact_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contact_messages_id_seq OWNED BY public.contact_messages.id;


--
-- Name: conversations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conversations (
    id uuid NOT NULL,
    user_id uuid,
    status character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.conversations OWNER TO postgres;

--
-- Name: dua_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dua_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean
);


ALTER TABLE public.dua_categories OWNER TO postgres;

--
-- Name: dua_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dua_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dua_categories_id_seq OWNER TO postgres;

--
-- Name: dua_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dua_categories_id_seq OWNED BY public.dua_categories.id;


--
-- Name: dua_favorites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dua_favorites (
    id integer NOT NULL,
    dua_id integer NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.dua_favorites OWNER TO postgres;

--
-- Name: dua_favorites_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dua_favorites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dua_favorites_id_seq OWNER TO postgres;

--
-- Name: dua_favorites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dua_favorites_id_seq OWNED BY public.dua_favorites.id;


--
-- Name: dua_views; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dua_views (
    id integer NOT NULL,
    dua_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    user_id uuid
);


ALTER TABLE public.dua_views OWNER TO postgres;

--
-- Name: dua_views_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dua_views_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dua_views_id_seq OWNER TO postgres;

--
-- Name: dua_views_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dua_views_id_seq OWNED BY public.dua_views.id;


--
-- Name: duas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.duas (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    arabic text NOT NULL,
    transliteration text,
    translation text,
    is_active boolean,
    notes text,
    benefits text,
    source text,
    featured boolean,
    category_id integer,
    view_count integer,
    favorite_count integer,
    audio_path character varying(512)
);


ALTER TABLE public.duas OWNER TO postgres;

--
-- Name: duas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.duas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.duas_id_seq OWNER TO postgres;

--
-- Name: duas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.duas_id_seq OWNED BY public.duas.id;


--
-- Name: files; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.files (
    id uuid NOT NULL,
    message_id uuid,
    file_name character varying(255),
    file_type character varying(50),
    file_size bigint,
    file_url character varying,
    uploaded_at timestamp without time zone
);


ALTER TABLE public.files OWNER TO postgres;

--
-- Name: hadith_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hadith_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean
);


ALTER TABLE public.hadith_categories OWNER TO postgres;

--
-- Name: hadith_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hadith_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hadith_categories_id_seq OWNER TO postgres;

--
-- Name: hadith_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hadith_categories_id_seq OWNED BY public.hadith_categories.id;


--
-- Name: hadith_favorites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hadith_favorites (
    id integer NOT NULL,
    hadith_id integer NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.hadith_favorites OWNER TO postgres;

--
-- Name: hadith_favorites_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hadith_favorites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hadith_favorites_id_seq OWNER TO postgres;

--
-- Name: hadith_favorites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hadith_favorites_id_seq OWNED BY public.hadith_favorites.id;


--
-- Name: hadith_views; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hadith_views (
    id integer NOT NULL,
    hadith_id integer NOT NULL,
    user_id uuid,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.hadith_views OWNER TO postgres;

--
-- Name: hadith_views_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hadith_views_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hadith_views_id_seq OWNER TO postgres;

--
-- Name: hadith_views_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hadith_views_id_seq OWNED BY public.hadith_views.id;


--
-- Name: hadiths; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hadiths (
    id integer NOT NULL,
    arabic text NOT NULL,
    translation text,
    narrator character varying(255),
    book character varying(255),
    number character varying(50),
    status character varying(50),
    rating double precision,
    category_id integer,
    is_active boolean,
    featured boolean,
    view_count integer,
    favorite_count integer
);


ALTER TABLE public.hadiths OWNER TO postgres;

--
-- Name: hadiths_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hadiths_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hadiths_id_seq OWNER TO postgres;

--
-- Name: hadiths_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hadiths_id_seq OWNED BY public.hadiths.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    sender_type character varying(10) NOT NULL,
    sender_id uuid,
    message_text text,
    message_type character varying(20),
    file_url character varying,
    status character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- Name: password_reset_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_reset_codes (
    id integer NOT NULL,
    user_id uuid,
    code character varying(6),
    expires_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.password_reset_codes OWNER TO postgres;

--
-- Name: password_reset_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.password_reset_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.password_reset_codes_id_seq OWNER TO postgres;

--
-- Name: password_reset_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.password_reset_codes_id_seq OWNED BY public.password_reset_codes.id;


--
-- Name: ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ratings (
    id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    rating integer NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.ratings OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying NOT NULL,
    username character varying NOT NULL,
    hashed_password character varying NOT NULL,
    avatar_url character varying,
    bio character varying,
    is_active boolean,
    is_verified boolean,
    role character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    reset_sent_at timestamp without time zone,
    latitude double precision,
    longitude double precision,
    city character varying,
    region character varying,
    country character varying,
    ip_address character varying,
    location_accuracy character varying,
    status character varying
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: zakat_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.zakat_records (
    id integer NOT NULL,
    user_id integer,
    name character varying,
    assets_total double precision NOT NULL,
    savings double precision NOT NULL,
    gold_price_per_gram double precision,
    nisab double precision,
    zakat_amount double precision NOT NULL,
    type character varying NOT NULL,
    note text,
    created_at timestamp without time zone
);


ALTER TABLE public.zakat_records OWNER TO postgres;

--
-- Name: zakat_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zakat_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.zakat_records_id_seq OWNER TO postgres;

--
-- Name: zakat_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zakat_records_id_seq OWNED BY public.zakat_records.id;


--
-- Name: allah_names id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allah_names ALTER COLUMN id SET DEFAULT nextval('public.allah_names_id_seq'::regclass);


--
-- Name: bookmarks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookmarks ALTER COLUMN id SET DEFAULT nextval('public.bookmarks_id_seq'::regclass);


--
-- Name: contact_messages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact_messages ALTER COLUMN id SET DEFAULT nextval('public.contact_messages_id_seq'::regclass);


--
-- Name: dua_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_categories ALTER COLUMN id SET DEFAULT nextval('public.dua_categories_id_seq'::regclass);


--
-- Name: dua_favorites id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_favorites ALTER COLUMN id SET DEFAULT nextval('public.dua_favorites_id_seq'::regclass);


--
-- Name: dua_views id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_views ALTER COLUMN id SET DEFAULT nextval('public.dua_views_id_seq'::regclass);


--
-- Name: duas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.duas ALTER COLUMN id SET DEFAULT nextval('public.duas_id_seq'::regclass);


--
-- Name: hadith_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_categories ALTER COLUMN id SET DEFAULT nextval('public.hadith_categories_id_seq'::regclass);


--
-- Name: hadith_favorites id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_favorites ALTER COLUMN id SET DEFAULT nextval('public.hadith_favorites_id_seq'::regclass);


--
-- Name: hadith_views id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_views ALTER COLUMN id SET DEFAULT nextval('public.hadith_views_id_seq'::regclass);


--
-- Name: hadiths id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadiths ALTER COLUMN id SET DEFAULT nextval('public.hadiths_id_seq'::regclass);


--
-- Name: password_reset_codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_codes ALTER COLUMN id SET DEFAULT nextval('public.password_reset_codes_id_seq'::regclass);


--
-- Name: zakat_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zakat_records ALTER COLUMN id SET DEFAULT nextval('public.zakat_records_id_seq'::regclass);


--
-- Data for Name: admin_notes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.admin_notes (id, conversation_id, admin_id, note_text, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.admin_users (id, name, email, password_hash, is_online, created_at) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
978d812655ea
\.


--
-- Data for Name: allah_names; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.allah_names (id, arabic, transliteration, meaning) FROM stdin;
1	الله	Allah	The Greatest Name
2	الرحمن	Ar-Rahman	The Most Merciful
3	الرحيم	Ar-Raheem	The Most Compassionate
4	الملك	Al-Malik	The King and Owner of Dominion
5	القدوس	Al-Quddus	The Absolutely Pure
6	السلام	As-Salaam	The Source of Peace and Safety
7	المؤمن	Al-Mu’min	The Giver of Faith and Security
8	المهيمن	Al-Muhaymin	The Guardian, The Witness
9	العزيز	Al-Aziz	The All Mighty
10	الجبار	Al-Jabbar	The Compeller, The Restorer
11	المتكبر	Al-Mutakabbir	The Supreme in Greatness
12	الخالق	Al-Khaliq	The Creator
13	البارئ	Al-Bari’	The Evolver, The Maker
14	المصور	Al-Musawwir	The Fashioner, The Shaper
15	الغفار	Al-Ghaffar	The All Forgiving
16	القهار	Al-Qahhar	The Subduer, The Dominant
17	الوهاب	Al-Wahhab	The Supreme Bestower
18	الرزاق	Ar-Razzaq	The Provider
19	الفتاح	Al-Fattah	The Opener, The Judge
20	العليم	Al-‘Aleem	The All-Knowing
21	القابض	Al-Qaabid	The Withholder
22	الباسط	Al-Baasit	The Expander
23	الخافض	Al-Khaafid	The Reducer
24	الرافع	Ar-Raafi’	The Exalter
25	المعز	Al-Mu‘izz	The Honourer, The Strengthener
26	المذل	Al-Mudhill	The Dishonourer, The Humiliator
27	السميع	As-Sami‘	The All-Hearing
28	البصير	Al-Baseer	The All-Seeing
29	الحكم	Al-Hakam	The Impartial Judge
30	العدل	Al-‘Adl	The Utterly Just
31	اللطيف	Al-Lateef	The Subtle One, The Most Gentle
32	الخبير	Al-Khabeer	The All-Aware
33	الحليم	Al-Haleem	The Forbearing, The Clement
34	العظيم	Al-‘Azeem	The Magnificent
35	الغفور	Al-Ghafoor	The Great Forgiver
36	الشكور	Ash-Shakoor	The Most Appreciative
37	العلي	Al-‘Aliyy	The Most High
38	الكبير	Al-Kabeer	The Most Great
39	الحفيظ	Al-Hafeez	The Preserver
40	المقيت	Al-Muqeet	The Sustainer
41	الحسيب	Al-Haseeb	The Reckoner
42	الجليل	Al-Jaleel	The Majestic
43	الكريم	Al-Kareem	The Generous
44	الرقيب	Ar-Raqeeb	The Watchful
45	المجيب	Al-Mujeeb	The Responsive
46	الواسع	Al-Waasi‘	The All-Encompassing
47	الحكيم	Al-Hakeem	The All-Wise
48	الودود	Al-Wadud	The Most Loving
49	المجيد	Al-Majeed	The Most Glorious
50	الباعث	Al-Ba‘ith	The Resurrector
51	الشهيد	Ash-Shaheed	The Witness
52	الحق	Al-Haqq	The Absolute Truth
53	الوكيل	Al-Wakeel	The Trustee, The Disposer of Affairs
54	القوي	Al-Qawiyy	The All-Strong
55	المتين	Al-Mateen	The Firm, The Steadfast
56	الولي	Al-Waliyy	The Protecting Friend
57	الحميد	Al-Hameed	The Praiseworthy
58	المحصي	Al-Muhsee	The Reckoner
59	المبدئ	Al-Mubdi’	The Originator
60	المعيد	Al-Mu‘eed	The Restorer
61	المحيي	Al-Muhyee	The Giver of Life
62	المميت	Al-Mumeet	The Creator of Death
63	الحي	Al-Hayy	The Ever-Living
64	القيوم	Al-Qayyum	The Sustainer of all existence
65	الواجد	Al-Waajid	The Finder
66	الماجد	Al-Maajid	The Illustrious
67	الواحد	Al-Waahid	The One
68	الصمد	As-Samad	The Eternal, The Absolute
69	القادر	Al-Qaadir	The Omnipotent
70	المقتدر	Al-Muqtadir	The Powerful
71	المقدم	Al-Muqaddim	The Expediter
72	المؤخر	Al-Mu’akhkhir	The Delayer
73	الأول	Al-Awwal	The First
74	الآخر	Al-Aakhir	The Last
75	الظاهر	Az-Zaahir	The Manifest
76	الباطن	Al-Baatin	The Hidden
77	الوالي	Al-Waali	The Governor
78	المتعالي	Al-Muta‘aali	The Most Exalted
79	البر	Al-Barr	The Source of Goodness
80	التواب	At-Tawwaab	The Accepter of Repentance
81	المنتقم	Al-Muntaqim	The Avenger
82	العفو	Al-‘Afuww	The Pardoner
83	الرؤوف	Ar-Ra’oof	The Compassionate
84	مالك الملك	Maalik-ul-Mulk	Owner of Sovereignty
85	ذو الجلال والإكرام	Dhul-Jalaali wal-Ikraam	Lord of Majesty and Generosity
86	المقسط	Al-Muqsit	The Just One
87	الجامع	Al-Jaami‘	The Gatherer
88	الغني	Al-Ghaniyy	The Self-Sufficient
89	المغني	Al-Mughni	The Enricher
90	المانع	Al-Maani‘	The Preventer
91	الضار	Ad-Daarr	The Distresser
92	النافع	An-Naafi‘	The Benefactor
93	النور	An-Noor	The Light
94	الهادي	Al-Haadi	The Guide
95	البديع	Al-Badee‘	The Incomparable
96	الباقي	Al-Baaqi	The Everlasting
97	الوارث	Al-Waarith	The Inheritor
98	الرشيد	Ar-Rasheed	The Guide to the Right Path
99	الصبور	As-Saboor	The Patient One
\.


--
-- Data for Name: bookmarks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bookmarks (id, user_id, ayah_key) FROM stdin;
1	dd29420b-3be3-4576-ac13-47edc63ab9bb	2:255
\.


--
-- Data for Name: chat_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_users (id, name, email, avatar_letter, created_at, last_seen, is_online) FROM stdin;
\.


--
-- Data for Name: contact_messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contact_messages (id, name, email, subject, message, created_at) FROM stdin;
\.


--
-- Data for Name: conversations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.conversations (id, user_id, status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dua_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dua_categories (id, name, description, is_active) FROM stdin;
5	Moring-dhikir		t
6	Evening-dhikir		t
\.


--
-- Data for Name: dua_favorites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dua_favorites (id, dua_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: dua_views; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dua_views (id, dua_id, created_at, user_id) FROM stdin;
\.


--
-- Data for Name: duas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.duas (id, title, arabic, transliteration, translation, is_active, notes, benefits, source, featured, category_id, view_count, favorite_count, audio_path) FROM stdin;
45	Sayyid al-Istighfar	اَللَّهُمَّ أَنْتَ رَبِّيْ ، لَا إِلٰـهَ إِلاَّ أَنْتَ خَلَقْتَنِيْ وَأَنَا عَبْدُكَ ، وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ ، أَعُوْذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ ، أَبُوْءُ لَكَ بِنِعْمتِكَ عَلَيَّ ، وَأَبُوْءُ بِذَنْبِيْ فَاغْفِرْ لِيْ ، فَإِنَّهُ لَا يَغْفِرُ الذُّنُوبَ إِلاَّ أَنْتَ	allahumma anta rabbi, la ilaha illa anta, khalaqtani wa ana 'abduka, wa ana 'ala 'ahdika wa wa'dika mastata'tu. a'udhu bika min sharri ma sana'tu, abu'u laka bini'matika 'alayya, wa abu'u bidhanbi faghfir li, fa innahu la yaghfir adh-dhunuba illa anta	O Allahm You are my Lord. There is no god but You. You created me I am your slave I stand firm in my promises and promises to you as much as possible. I seek refuge in You from the evil of my deeds. I acknowledge my sin. So forgive me. Because there is no one who forgives sins except You.	t	Recite 1x	Whoever reads it with confidence in the evening, then he dies, he will enter heaven, so also if (read) in the morning.	HR. al-Bukhari No. 6306, 6323, Ahmad IV/122-125, an-Nasa'i VIII/279-280	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
39	Ayatul Kursi	ٱللَّهُ لَآ إِلَٰهَ إِلَّا هُوَ ٱلْحَىُّ ٱلْقَيُّومُ ۚ لَا تَأْخُذُهُۥ سِنَةٌ وَلَا نَوْمٌ ۚ لَّهُۥ مَا فِى ٱلسَّمَٰوَٰتِ وَمَا فِى ٱلْأَرْضِ ۗ مَن ذَا ٱلَّذِى يَشْفَعُ عِندَهُۥٓ إِلَّا بِإِذْنِهِۦ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَىْءٍ مِّنْ عِلْمِهِۦٓ إِلَّا بِمَا شَآءَ ۚ وَسِعَ كُرْسِيُّهُ ٱلسَّمَٰوَٰتِ وَٱلْأَرْضَ ۖ وَلَا يَـُٔودُهُۥ حِفْظُهُمَا ۚ وَهُوَ ٱلْعَلِىُّ ٱلْعَظِيمُ	allahu la ilaha illa huwa, al-hayyul-qayyum. la ta'khudhuhu sinatun wa la nawm. lahu ma fis-samawati wa ma fil-ard. man dhal-ladhi yashfa'u 'indahu illa bi-idhnihi. ya'lamu ma bayna aydihim wa ma khalfahum. wa la yuhiytuna bishay'in min 'ilmihi illa bima shaa'. wa si'a kursiyyuhu as-samawati wal-ard. wa la ya'udu-hu hifdhuhuma. wa huwa al-'aliyyul-'azim	Allah - there is no deity except Him, the Ever-Living, the Sustainer of [all] existence. Neither drowsiness overtakes Him nor sleep. To Him belongs whatever is in the heavens and whatever is on the earth. Who is it that can intercede with Him except by His permission? He knows what is [presently] before them and what will be after them, and they encompass not a thing of His knowledge except for what He wills. His Kursi extends over the heavens and the earth, and their preservation tires Him not. And He is the Most Hight, the Most Great.	t	Recite 1x	Whoever reads this verse in the morning, he will be protected until evening. And whoever reads it in the evening, he will be protected until morning.	HR. at-Tirmidzi: 2879	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
40	Al-Ikhlas	قُلْ هُوَ ٱللَّهُ أَحَدٌ (1) ٱللَّهُ ٱلصَّمَدُ (2) لَمْ يَلِدْ وَلَمْ يُولَدْ (3) وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌۢ (4)	qul huwa allahu ahad (1) allahu samad (2) lam yalid wa lam yulad (3) wa lam yakun lahu kufuwan ahad (4)	Say, O Prophet, He is Allah - One and Indivisible (1) Allah - the Sustainer needed by all (2) He has never had offspring, nor was He born (3) And there is none comparable to Him (4).	t	Recite 3x	Rasulullah shallallahu 'alaihi wa sallam said: Say (read the surahs), Qulhuwallahu ahad, and Al-Muawwidzatain (Al-Falaq & An-Naas) three times in the evening and morning, then these verses will suffice you (guard you) from evening.	HR. Abu Dawud No. 4241	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
41	Al-Falaq	قُلْ أَعُوذُ بِرَبِّ ٱلْفَلَقِ (1) مِن شَرِّ مَا خَلَقَ (2) وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ (3) وَمِن شَرِّ ٱلنَّفَّٰثَٰتِ فِى ٱلْعُقَدِ (4) وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ (5)	qul a'udhu birabbil-falaq (1) min sharri ma khalaq (2) wa min sharri ghaasiqin idha waqab (3) wa min sharri naffathati fil-'uqad (4) wa min sharri hasidin idha hasad (5)	Say, O Prophet, I seek refuge in the Lord of the daybreak (1) from the evil of whatever He has created (2) and from the evil of the night when it grows dark (3) and from the evil of those ˹witches casting spells by˺ blowing onto knots (4) and from the evil of an envier when they envy (5)	t	Recite 3x	Rasulullah shallallahu 'alaihi wa sallam said: Say (read the surahs), Qulhuwallahu ahad, and Al-Muawwidzatain (Al-Falaq & An-Naas) three times in the evening and morning, then these verses will suffice you (guard you) from evening.	HR. Abu Dawud No. 4241	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
42	An-Naas	قُلْ أَعُوذُ بِرَبِّ ٱلنَّاسِ (1) مَلِكِ ٱلنَّاسِ (2) إِلَٰهِ ٱلنَّاسِ (3) مِن شَرِّ ٱلْوَسْوَاسِ ٱلْخَنَّاسِ (4) ٱلَّذِى يُوَسْوِسُ فِى صُدُورِ ٱلنَّاسِ (5) مِنَ ٱلْجِنَّةِ وَٱلنَّاسِ (6)	qul a'udhu birabbin-naas (1) malikin-naas (2) ilahin-naas (3) min sharri al-waswasi al-khannas (4) alladhi yuwaswisu fi sudoorin-naas (5) mina al-jinnati wan-naas (6)	Say, O Prophet, I seek refuge in the Lord of humankind (1) the Master of humankind (2) the God of humankind (3) from the evil of the lurking whisperer (4) who whispers into the hearts of humankind (5) from among jinn and humankind (6)	t	Recite 3x	Rasulullah shallallahu 'alaihi wa sallam said: Say (read the surahs), Qulhuwallahu ahad, and Al-Muawwidzatain (Al-Falaq & An-Naas) three times in the evening and morning, then these verses will suffice you (guard you) from evening.	HR. Abu Dawud No. 4241	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
43	Upon Entering The Morning by Asking for Protection from Allah	أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لاَ إِلَـهَ إِلاَّ اللهُ وَحْدَهُ لاَ شَرِيْكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيْرُ. رَبِّ أَسْأَلُكَ خَيْرَ مَا فِيْ هَذَا الْيَوْمِ وَخَيْرَ مَا بَعْدَهُ، وَأَعُوْذُ بِكَ مِنْ شَرِّ مَا فِيْ هَذَا الْيَوْمِ وَشَرِّ مَا بَعْدَهُ، رَبِّ أَعُوْذُ بِكَ مِنَ الْكَسَلِ وَسُوْءِ الْكِبَرِ، رَبِّ أَعُوْذُ بِكَ مِنْ عَذَابٍ فِي النَّارِ وَعَذَابٍ فِي الْقَبْرِ	asbahna wa-asbaha al-mulku lillahi, wal-hamdu lillahi, la ilaha illa allah wahdahu la sharika lahu, lahu al-mulku wa lahu al-hamdu wa huwa 'ala kulli shay'in qadir. rabbi as'aluka khayra ma fi hadha al-yawm wa khayra ma ba'dahu, wa a'udhu bika min sharri ma fi hadha al-yawm wa sharri ma ba'dahu. rabbi a'udhu bika mina al-kasali wa su'il-kibar. rabbi a'udhu bika min 'adabin fin-nar wa 'adabin fil-qabr	We have entered the morning time and the kingdom belongs to Allah. There is no god who has the right to be worshiped properly except Allah almighty, there is no partner for Him. For Him is the kingdom and praise is for Him. He- is the Almighty over all things. O Lord, I ask You for the good of this day and the good after it. I seek refuge in You from the evil of this day and the evil after it. O Lord, I seek refuge in You from torments of Hell and the torments of the grave.	t	Recite 1x	Asking for protection from evil takes precedence, the rule that shows the importance of this is: "Preventing harm is more important and takes precedence than bringing good".	HR. Muslim No. 2723 (75), Abu Dawud No. 5071, and at-Tirmidzi 3390, shahih from Abdullah Ibnu Mas'ud	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
44	Upon Entering The Morning with The Grace of Allah	اَللَّهُمَّ بِكَ أَصْبَحْنَا، وَبِكَ أَمْسَيْنَا، وَبِكَ نَحْيَا، وَبِكَ نَمُوْتُ وَإِلَيْكَ النُّشُوْرُ	allahumma bika asbahna, wa bika amsayna, wa bika nahya, wa bika namutu wa ilayka an-nushoor	O Allah, with Your grace and help we enter the morning, and with Your grace and help we enter the evening. By Your grace and will we live and by Your grace and will we die. And to You is the resurrection (for all creatures).	t	Recite 1x	Everything we do from morning to evening, from when we start our life until we die, is all under the control of Allah and to Him we return.	HR. al-Bukhari in al-Abadul Mufrad No. 1199, this lafazh is lafazh al-Bukhari, at-Tirmidzi No. 3391, Abu Dawud No. 5068, Ahmad 11/354, Ibnu Majah No. 3868	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
46	Dua for Protection and Good Health	اَللَّهُمَّ عَافِنِيْ فِيْ بَدَنِيْ ، اَللَّهُمَّ عَافِنِيْ فِيْ سَمْعِيْ ، اَللَّهُمَّ عَافِنِيْ فِيْ بَصَرِيْ ، لَا إِلَـهَ إِلَّا أَنْتَ ، اَللَّهُمَّ إِنِّيْ أَعُوْذُ بِكَ مِنَ الْكُفْرِوَالْفَقْرِ ، وَأَعُوْذُ بِكَ مِنْ عَذَابِ الْقَبْرِ ، لَا إِلَـهَ إِلَّا أَنْتَ	allahumma 'afini fi badani, allahumma 'afini fi sam'i, allahumma 'afini fi basari, la ilaha illa anta, allahumma inni a'udhu bika min al-kufri wal-faqr, wa a'udhu bika min 'adhabi al-qabr, la ilaha illa anta	O Allah, save my body (from disease and from what I don't want). O Allah, save my hearing (from disease and immorality or from what I don't want). O Allah, save my sight, there is no deity who has the right to be worshiped with righteous except You. O Allah, verily I seek refuge in You from disbelief and neediness. I seek refuge in You from the torment of the grave, there is no deity who has the right to be worshiped properly except You.	t	Recite 1x	By asking Allah to grant us well-being in our body, we are asking to be cured from all physical and spritual ailments, so that we possess both a healthy body and a pure heart, and therefore use this healthy body in a way that pleases Allah.	HR. al-Bukhari n Shahiib al-Adabil Mufrad No. 701, Abu Dawud No. 5090, Ahmad V/42, hasan	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
47	Dua for Salvation in The World and Hereafter	اَللَّهُمَّ إِنِّيْ أَسْأَلُكَ الْعَفْوَ وَالْعَافِيَةَ فِي الدُّنْيَا وَاْلآخِرَةِ، اَللَّهُمَّ إِنِّيْ أَسْأَلُكَ الْعَفْوَ وَالْعَافِيَةَ فِي دِيْنِيْ وَدُنْيَايَ وَأَهْلِيْ وَمَالِيْ اللَّهُمَّ اسْتُرْ عَوْرَاتِى وَآمِنْ رَوْعَاتِى. اَللَّهُمَّ احْفَظْنِيْ مِنْ بَيْنِ يَدَيَّ، وَمِنْ خَلْفِيْ، وَعَنْ يَمِيْنِيْ وَعَنْ شِمَالِيْ، وَمِنْ فَوْقِيْ، وَأَعُوْذُ بِعَظَمَتِكَ أَنْ أُغْتَالَ مِنْ تَحْتِيْ	allahumma inni as'aluka al-'afwa wal-'afiyata fi'd-dunya wa'l-akhirah. allahumma inni as'aluka al-'afwa wal-'afiyata fi deeni wa dunyaya wa ahli wa mali. allahumma istur 'awraati wa amin raw'aaati. allahumma ihfazni min bayni yadayya, wa min khalfi, wa 'an yameeni wa 'an shimaali, wa min fawqi. wa a'udhu bi 'azamatika an ughtala min tahti	O Allah, I really ask for goodness and safety in this world and the hereafter. O Allah, I really ask for goodness and safety in religion, the world, my family and wealth. O Allah, cover my nakedness (disgrace and something that is not suitable for people to see) and calm me save me from fear. O Allah, protect me from in front, behind, right, left and above me. I seek protection from Your greatness, so that I will not be grabbed from under me (I seek protection from being immersed in the earth).	t	Recite 1x	The Prophet shallallahu 'alaihi wa sallam never left this prayer in the morning and evening. It contains protection and safety for religion, the world, family and property from various kinds of disturbances that come from various directions.	HR. al-Bukhari in al-Abadul Mufrad No. 1200, Abu Dawud No. 5074, an-Nasa'i VII/282, Ibnu Majah No. 3871, al-Hakim 1/517-518, and others from Ibnu Umar radhiyallahu 'anhumaa	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
48	Dua for Protection from Shaytan Whispers	اَللَّهُمَّ عَالِمَ الْغَيْبِ وَالشَّهَادَةِ فَاطِرَ السَّمَاوَاتِ وَاْلأَرْضِ، رَبَّ كُلِّ شَيْءٍ وَمَلِيْكَهُ، أَشْهَدُ أَنْ لاَ إِلَـهَ إِلاَّ أَنْتَ، أَعُوْذُ بِكَ مِنْ شَرِّ نَفْسِيْ، وَمِنْ شَرِّ الشَّيْطَانِ وَشِرْكِهِ، وَأَنْ أَقْتَرِفَ عَلَى نَفْسِيْ سُوْءًا أَوْ أَجُرَّهُ إِلَى مُسْلِمٍ	allahumma 'alimal-ghaybi wash-shahadati, fatiras-samawati wal-ard, rabbakulli shayin wa malikahu. ashhadu alla ilaha illa anta, a'udhu bika min sharri nafsi, wa min sharri ash-shaytani wa shirkih. wa an aqtarifa 'ala nafsi su'an aw ajurrahu ila muslim	O Allah, Who knows the unseen and the real. O Lord, Creator of the heavens and the earth, Lord of all things and Who reigns over them. I testify that there is no god who has the right to be worshiped properly except You. I seek refuge in You from the evil of myself, satan and his invitation to associate partners with Allah, (I seek refuge in You) from doing evil to me or pushing a Muslim against him.	t	Recite 1x	The Prophet Muhammad shallallahu 'alaihi wa sallam said to Abu Bakr ash-Shiddiq radhiyallahu 'anhu 'Say morning and evening and when you are going to sleep'.	HR. al-Bukhari in al-Abadul Mufrad No. 1202, at-Tirmidzi No. 3392 and Abu Dawud No. 5067	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
49	Asking for Protection from All Harms	بِسْمِ اللَّهِ الَّذِى لاَ يَضُرُّ مَعَ اسْمِهِ شَىْءٌ فِى الأَرْضِ وَلاَ فِى السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ	bismillahi alladhi la yadurru ma'asmihi shay'un fi'l-ard wa la fi's-sama'i, wa huwa as-sami'u al-'aleem	In the name of Allah with Whose name nothing can harm on earth or in heaven, and He is the All-Hearing, All-Knowing.	t	Recite 3x	Whoever reads it three times in the morning and evening, then nothing will harm him.	HR. at-Tirmidzi No. 3388, Abu Dawud No. 5088, Ibnu Majah No. 3869, al-Hakim 1/514, and Ahmad No. 446 and 474	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
50	Declaration of Pleasure with Allah, Islam, and the Prophet Muhammad shallallahu 'alaihi wa sallam	رَضِيْتُ بِاللهِ رَبًّا، وَبِاْلإِسْلاَمِ دِيْنًا، وَبِمُحَمَّدٍ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ نَبِيًّا	radi'tu billahi rabban, wa bil-Islami deenan, wa bi-muhammadin sallallahu 'alayhi wa sallam nabiyyan	I am willing (pleased) Allah as my Rabb (for me and others), Islam as my religion and Muhammad shallallahu 'alaihi wa sallam as my Prophet (sent by Allah).	t	Recite 3x	Whoever reads it three times in the morning and evening, Allah will give His pleasure to him and the Day of Judgment.	HR. Ahmad IV/337, Abu Dawud No. 5072, at-Tirmidzi No. 3389, Ibnu Majah No. 3870, an-Nasa'i in 'Amalul Yaum wal Lailah No. 4 and Ibnus Sunni No. 68	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
51	Asking Allah for Guidance	يَا حَيُّ يَا قَيُّوْمُ بِرَحْمَتِكَ أَسْتَغِيْثُ، وَأَصْلِحْ لِيْ شَأْنِيْ كُلَّهُ وَلاَ تَكِلْنِيْ إِلَى نَفْسِيْ طَرْفَةَ عَيْنٍ أَبَدًا	ya hayyu ya qayyum, bi rahmatika astagheeth. wa aslih li shani kullahu wa la takilni ila nafsi tarfata 'aynin abadan	O Rabb of the Most Living, O Rabb of the Most Self-sufficient (does not need anything) with Your grace I ask for help, fix all my affairs and do not leave (my affairs) to myself even if only for the twinkling of an eye (without getting help from You).	t	Recite 1x	The meaning of this prayer is that humans really need Allah and pray that Allah will not leave him even for a moment.	HR. an-Nasa'i in 'Amalul Yaum wal Lailah No. 575, and al-Hakim 1/545, Shahiih at-Targhiib wat Tarhiib 1/417 No. 661, Ash-shahiihah No. 227, hasan	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
52	Entering The Morning Upon The Natural Religion of Islam	أَصْبَحْنَا عَلَى فِطْرَةِ اْلإِسْلاَمِ وَعَلَى كَلِمَةِ اْلإِخْلاَصِ، وَعَلَى دِيْنِ نَبِيِّنَا مُحَمَّدٍ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ، وَعَلَى مِلَّةِ أَبِيْنَا إِبْرَاهِيْمَ، حَنِيْفًا مُسْلِمًا وَمَا كَانَ مِنَ الْمُشْرِكِيْنَ	asbahnā 'alā fiṭraṭi al-Islāmi wa 'alā kalimati al-iKhlāṣi, wa 'alā dīni nabīninā muḥammadin ṣallā allāhu 'alayhi wa sallam, wa 'alā millati abīnā ibrāhīma, ḥanīfan musliman wa mā kāna min al-mushrikīn	In the morning we are above the nature of the Islamic religion, sincere sentences, the religion of our Prophet Muhammad shallallahu 'alaihi wa sallam and the religion of our father, Ibrahim, who stands on the straight path, is Muslim and is not classified as polytheists.	t	Recite 1x	'Fitratil Islam' means above the sunnah, 'kalimatil Ikhlas' means the Syahadah and 'hanifan' means the heart is inclined to the straight path and goodness.	HR. Ahmad III/406, 407, ad-Darimi II/292 and Ibnus Sunni in Amalul Yaum wal Lailah No. 34, Misykaatul Mashaabiih No. 2415, Shahiihal-Jaami'ish Shaghiir No. 4674, shahih	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
53	Tawheed Dhikr	لاَ إِلَـهَ إِلاَّ اللهُ وَحْدَهُ لاَ شَرِيْكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيْرُ	la ilaha illallah, wahdahu la sharika lah, lahu al-mulku wa lahu al-hamdu, wa huwa 'ala kulli shay'in qadir	There is no God who has the right to be worshiped properly except Allah, the One and Only, He has no partners. For Him is the kingdom and for Him is all praise. And He is Almighty over all things.	t	Recite 1x or 10x in the morning, Recite 100x a day	Whoever reads it 100 times a day, then for him (the reward) is like freeing ten slaves, writing a hundred good things, removing a hundred bad things from him, getting protection from the devil that day until the evening. It is not that a person can bring better than what he brought unless he did more than that.	HR al-Bukhari No. 3293 and 6403, Muslim IV/2071 No. 2691 (28), at-Tirmidzi No. 3468, Ibnu Majah No. 3798	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
54	Read Tasbih	سُبْحَانَ اللهِ وَبِحَمْدِهِ عَدَدَ خَلْقَهِ وَرِضَى نَفْسِهِ وَزِنَةَ عَرْشِهِ وَمِدَادَ كَلِمَاتِهِ	subhanallah wa bihamdihi, 'adada khalqihi wa ridha nafsihi, wazinata 'arshihi, wa midad kalimatihi	Glory to Allah, I praise Him as many as the number of His creatures, Glory to Allah according to His pleasure, as pure as the weight of His Throne, and as pure as the ink (which writes) His words.	t	Recite 3x	The Prophet shallallahu 'alaihi wa sallam told Juwairiyah that the dhikr above had defeated the dhikr Read by Juwairiyah from after Fajr to Duha time.	HR. Muslim No. 2726. Syarah Muslim XVII/44. From Juwairiyah binti al-Harits radhiyallahu 'anhuma	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
55	Dua for Useful Knowledge, Good Sustenance, and Accepted Deeds	اللَّهُمَّ إِنِّى أَسْأَلُكَ عِلْمًا نَافِعًا وَرِزْقًا طَيِّبًا وَعَمَلاً مُتَقَبَّلاً	allahumma inni as'aluka 'ilman nafi'an, wa rizqan tayyiban, wa 'amalan mutaqabbalan	O Allah, I really ask You for knowledge that is beneficial, sustenance that is lawful, and deeds that are accepted.	t	Recite 1x	This prayer is recommended in the morning because morning time has more privileges and blessings. as the words of Rasulullah shallallahu 'alaihi wa sallam "O Allah, bless my people in the morning".	HR. Ibnu Majah No. 925, Shahiih Ibni Majah 1/152 No. 753 Ibnus Sunni in 'Amalul Yaum wal Lailah No. 54, 110, and Ahmad VI/294, 305, 318, 322. From Ummu Salamah, shahih	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
56	Daily Tasbih and Tahmid	سُبْحَانَ اللَّهِ وَبِحَمْدِهِ	subhanallah wa bihamdihi	Glory be to Allah, I praise Him.	t	Recite 100x	Whoever says the phrase 'subhanallah wa bi hamdih' in the morning and evening 100 times, then no one will come on the Day of Judgement that is better than what he did except the person who said something like or more thant that.	HR. Muslim No. 2691 and No. 2692, from Abu Hurairah radhiyallahu 'anhu Syarah Muslim XVII/17-18, Shahiih at-Targhiib wat Tarhiib 1/413 No. 653	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
57	Istighfar 100x a Day	أَسْتَغْفِرُ الله وَأَتُوْبُ إِلَيْهِ	astaghfiru Allah wa atubu ilayhi	I seek forgiveness from Allah and repent to Him.	t	Recite 100x a day	From Ibn 'Umar he said: The Mesengger of Allah Muhammad shallallahu 'alaihi wa sallam said: 'O people, repent to Allah, in fact I repent to Him a hundred times a day'.	HR. al-Bukhari/Fat-hul Baari XI/101 and Muslim No. 2702	f	5	0	0	/static/audio/category_5_Moring_dhikr.mp3
59	Al-Ikhlas	قُلْ هُوَ ٱللَّهُ أَحَدٌ (1) ٱللَّهُ ٱلصَّمَدُ (2) لَمْ يَلِدْ وَلَمْ يُولَدْ (3) وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌۢ (4)	qul huwallāhu aḥad (1) allāhuṣ-ṣamad (2) lam yalid wa lam yụlad (3) wa lam yakul lahụ kufuwan aḥad (4)	Say, "He is Allah , [who is] One, (1) Allah , the Eternal Refuge. (2) He neither begets nor is born, (3) Nor is there to Him any equivalent." (4)	t	Read 3x	The Messenger of Allah, peace and blessings be upon him, said: Recite Qul huwallahu ahad, and Al-Mu'awwidhatayn (Al-Falaq and An-Nas) in the evening and morning three times, and it will suffice you (protect you) from everything.	HR. Abu Dawud No. 4241	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
58	Ayat al-Kursi	ٱللَّهُ لَآ إِلَٰهَ إِلَّا هُوَ ٱلْحَىُّ ٱلْقَيُّومُ ۚ لَا تَأْخُذُهُۥ سِنَةٌ وَلَا نَوْمٌ ۚ لَّهُۥ مَا فِى ٱلسَّمَٰوَٰتِ وَمَا فِى ٱلْأَرْضِ ۗ مَن ذَا ٱلَّذِى يَشْفَعُ عِندَهُۥٓ إِلَّا بِإِذْنِهِۦ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيْطُونَ بِشَىْءٍ مِّنْ عِلْمِهِۦٓ إِلَّا بِمَا شَآءَ ۚ وَسِعَ كُرْسِيُّهُ ٱلسَّمَٰوَٰتِ وَٱلْأَرْضَ ۖ وَلَا يَـُٔودُهُۥ حِفْظُهُمَا ۚ وَهُوَ ٱلْعَلِىُّ ٱلْعَظِيمُ	Allāhu lā ilāha illā huw, al-ḥayyul-qayyụm, lā ta`khużuhụ sinatuw wa lā na`ụm, lahụ mā fis-samāwāti wa mā fil-arḍ, man żallażī yasyfa'u 'indahū illā bi`iżnih, ya'lamu mā baina aidīhim wa mā khalfahum, wa lā yuḥīṭụna bisyai`im min 'ilmihī illā bimā syā`, wasi'a kursiyyuhus-samāwāti wal-arḍ, wa lā ya`ụduhụ ḥifẓuhumā, wa huwal-'aliyyul-'aẓīm	Allah - there is no deity except Him, the Ever-Living, the Sustainer of [all] existence. Neither drowsiness overtakes Him nor sleep. To Him belongs whatever is in the heavens and whatever is on the earth. Who is it that can intercede with Him except by His permission? He knows what is [presently] before them and what will be after them, and they encompass not a thing of His knowledge except for what He wills. His Kursi extends over the heavens and the earth, and their preservation tires Him not. And He is the Most High, the Most Great.	t	Read 1x	Whoever recites this verse in the morning will be protected until the evening. And whoever recites it in the evening will be protected until the morning.	HR. at-Tirmidzi: 2879	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
60	Al-Falaq	قُلْ أَعُوذُ بِرَبِّ ٱلْفَلَقِ (1) مِن شَرِّ مَا خَلَقَ (2) وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ (3) وَمِن شَرِّ ٱلنَّفَّٰثَٰتِ فِى ٱلْعُقَدِ (4) وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ (5)	qul a'ụżu birabbil-falaq (1) min syarri mā khalaq (2) wa min syarri gāsiqin iżā waqab (3) wa min syarrin-naffāṡāti fil-'uqad (4) wa min syarri ḥāsidin iżā ḥasad (5)	Say, "I seek refuge in the Lord of daybreak (1) From the evil of that which He created (2) And from the evil of darkness when it settles (3) And from the evil of the blowers in knots (4) And from the evil of an envier when he envies." (5)	t	Read 3x	The Messenger of Allah, peace and blessings be upon him, said: Recite Qul huwallahu ahad, and Al-Mu'awwidhatayn (Al-Falaq and An-Nas) in the evening and morning three times, and it will suffice you (protect you) from everything.	HR. Abu Dawud No. 4241	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
61	An-Naas	قُلْ أَعُوذُ بِرَبِّ ٱلنَّاسِ (1) مَلِكِ ٱلنَّاسِ (2) إِلَٰهِ ٱلنَّاسِ (3) مِن شَرِّ ٱلْوَسْوَاسِ ٱلْخَنَّاسِ (4) ٱلَّذِى يُوَسْوِسُ فِى صُدُوْرِ ٱلنَّاسِ (5) مِنَ ٱلْجِنَّةِ وَٱلنَّاسِ (6)	qul a'ụżu birabbin-nās (1) malikin-nās (2) ilāhin-nās (3) min syarril-waswāsil-khannās (4) allażī yuwaswisu fī ṣudụrin-nās (5) minal-jinnati wan-nās (6)	Say, "I seek refuge in the Lord of mankind, (1) The King of mankind. (2) The God of mankind, (3) From the evil of the whisperer who withdraws, (4) Who whispers in the breasts of mankind, (5) Of the jinn and mankind." (6)	t	Read 3x	The Messenger of Allah, peace and blessings be upon him, said: Recite Qul huwallahu ahad, and Al-Mu'awwidhatayn (Al-Falaq and An-Nas) in the evening and morning three times, and it will suffice you (protect you) from everything.	HR. Abu Dawud No. 4241	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
62	Entering the Evening in the Kingdom of Allah and Seeking His Protection	أَمْسَيْنَا وَأَمْسَى الْمُلْكُ للهِ، وَالْحَمْدُ للهِ، لَا إِلَهَ إِلاَّ اللهُ وَحْدَهُ لاَ شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ، وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ، رَبِّ أَسْأَلُكَ خَيْرَ مَا فِي هَذِهِ اللَّيْلَةِ وَخَيْرَ مَا بَعْدَهَا، وَأَعُوذُبِكَ مِنْ شَرِّ مَا فِي هَذِهِ اللَّيْلَةِ وَشَرِّ مَا بَعْدَهَا، رَبِّ أَعُوذُبِكَ مِنَ الْكَسَلِ وَسُوءِ الْكِبَرِ، رَبِّ أَعُوذُبِكَ مِنْ عَذَابٍ فِي النَّارِ وَعَذَابٍ فِي الْقَبْرِ	amsaynaa wa amsal mulku lillah walhamdulillah, laa ilaha illallah wahdahu laa syarika lah, lahul mulku walahul hamdu wa huwa 'ala kulli syai-in qodir. robbi as-aluka khoiro maa fii hadzihil lailah wa khoiro maa ba'dahaa, wa a'udzu bika min syarri maa fii hadzihil lailah wa syarri maa ba'dahaa. robbi a'udzu bika minal kasali wa suu-il kibar. robbi a'udzu bika min 'adzabin fin naari wa 'adzabin fil qobri	We have entered the evening and the dominion belongs to Allah, and all praise is for Allah. There is no deity worthy of worship except Allah alone, He has no partner. To Him belongs the dominion and to Him is praise, and He is over all things competent. My Lord, I ask You for the good of this night and the good of what follows it, and I seek refuge in You from the evil of this night and the evil of what follows it. My Lord, I seek refuge in You from laziness and the evil of old age. My Lord, I seek refuge in You from the punishment of the Fire and the punishment of the grave.	t	Read 1x	Seeking protection from evil is prioritized, the principle that shows the importance of this is: "Preventing harm is more important and prioritized than bringing about good."	HR. Muslim No. 2723 (75), Abu Dawud No. 5071, and at-Tirmidzi 3390, sahih from Abdullah Ibn Mas'ud	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
63	Entering the Evening by Seeking Allah's Mercy	اللَّهُمَّ بِكَ أَمْسَيْنَا، وَبِكَ أَصْبَحْنَا،وَبِكَ نَحْيَا، وَبِكَ نَمُوتُ، وَإِلَيْكَ الْمَصِيْرُ	allahumma bika amsaynaa wa bika ash-bahnaa wa bika nahyaa wa bika namuutu wa ilaikal mashiir	O Allah, by Your grace and help we have entered the evening, and by Your grace and help we enter the morning. By Your grace and help we live and by Your will we die. And to You is the final return (of all creatures).	t	Read 1x	Everything we do from morning to evening, from the beginning of our lives until we die, is all under Allah's control and to Him we return.	HR. al-Bukhari in al-Abadul Mufrad No. 1199, this wording is the wording of al-Bukhari at-Tirmidzi No. 3391, Abu Dawud No. 5068, Ahmad 11/354, Ibn Majah No. 3868	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
64	The Master of Seeking Forgiveness	اَللَّهُمَّ أَنْتَ رَبِّيْ ، لَا إِلٰـهَ إِلاَّ أَنْتَ خَلَقْتَنِيْ وَأَنَا عَبْدُكَ ، وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ ، أَعُوْذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ ، أَبُوْءُ لَكَ بِنِعْمتِكَ عَلَيَّ ، وَأَبُوْءُ بِذَنْبِيْ فَاغْفِرْ لِيْ ، فَإِنَّهُ لَا يَغْفِرُ الذُّنُوْبَ إِلاَّ أَنْتَ	allahumma anta rabbii laa ilaaha illaa anta khalaqtanii wa anna 'abduka wa anaa 'alaa 'ahdika wa wa'dika mastatha'tu a'uudzu bika min syarri maa shana'tu abuu u laka bini' matika 'alayya wa abuu-u bidzanbii faghfir lii fa innahu laa yaghfirudz dzunuuba illa anta	O Allah, You are my Lord, there is no deity worthy of worship except You, You created me and I am Your servant. I will be true to my covenant and promise to You as much as I can. I seek refuge in You from the evil of what I have done. I acknowledge Your favor upon me and I acknowledge my sin, therefore, forgive me. Indeed, there is no one who can forgive sins except You.	t	Read 1x	Whoever recites it with certainty in the evening, and then he dies, he will enter Paradise, and likewise if (recited) in the morning.	HR. al-Bukhari No. 6306, 6323, Ahmad IV/122-125, an-Nasa'i VIII/279-280	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
65	Prayer for Health and Protection	اَللَّهُمَّ عَافِنِيْ فِيْ بَدَنِيْ ، اَللَّهُمَّ عَافِنِيْ فِيْ سَمْعِيْ ، اَللَّهُمَّ عَافِنِيْ فِيْ بَصَرِيْ ، لَا إِلَـهَ إِلَّا أَنْتَ ، اَللَّهُمَّ إِنِّيْ أَعُوْذُ بِكَ مِنَ الْكُفْرِ وَالْفَقْرِ ، وَأَعُوْذُ بِكَ مِنْ عَذَابِ الْقَبْرِ ، لَا إِلَـهَ إِلَّا أَنْتَ	allaahumma 'aafinii fii badanii, allaahumma 'aafinii fii sam'ii, allaahumma 'aafinii fii bashorii, laa ilaaha illaa anta. allaahumma inni a'uudzu bika minal kufri wal faqr, allaahumma inni a'uudzu bika min 'adzaabil qobr, laa ilaaha illaa anta	O Allah, protect my body (from illness and from what I do not want). O Allah, protect my hearing (from illness and disobedience or from what I do not want). O Allah, protect my sight, there is no deity worthy of worship except You. O Allah, indeed I seek refuge in You from disbelief and poverty. I seek refuge in You from the punishment of the grave, there is no deity worthy of worship except You.	t	Read 1x	By asking Allah to grant us well-being in our bodies, we ask to be healed from all physical and spiritual illnesses, so that we have a healthy body and a pure heart, and therefore use this healthy body in a way that pleases Allah.	HR. al-Bukhari in Shahiib al-Adabil Mufrad No. 701, Abu Dawud No. 5090, Ahmad V/42, hasan	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
66	Prayer for Safety in This World and the Hereafter	اَللَّهُمَّ إِنِّيْ أَسْأَلُكَ الْعَفْوَ وَالْعَافِيَةَ فِي الدُّنْيَا وَاْلآخِرَةِ، اَللَّهُمَّ إِنِّيْ أَسْأَلُكَ الْعَفْوَ وَالْعَافِيَةَ فِي دِيْنِيْ وَدُنْيَايَ وَأَهْلِيْ وَمَالِيْ اللَّهُمَّ اسْتُرْ عَوْرَاتِى وَآمِنْ رَوْعَاتِى. اَللَّهُمَّ احْفَظْنِيْ مِنْ بَيْنِ يَدَيَّ، وَمِنْ خَلْفِيْ، وَعَنْ يَمِيْنِيْ وَعَنْ شِمَالِيْ، وَمِنْ فَوْقِيْ، وَأَعُوْذُ بِعَظَمَتِكَ أَنْ أُغْتَالَ مِنْ تَحْتِيْ	allahumma innii as-alukal 'afwa wal 'aafiyah fid dunyaa wal aakhiroh. allahumma innii as-alukal 'afwa wal 'aafiyah fii diinii wa dun-yaaya wa ahlii wa maalii. allahumas-tur 'awrootii wa aamin row'aatii. allahummahfazh-nii mim bayni yadayya wa min kholfii wa 'an yamiinii wa 'an syimaalii wa min fawqii wa a'udzu bi 'azhomatik an ugh-taala min tahtii	O Allah, indeed I ask You for well-being and safety in this world and the Hereafter. O Allah, indeed I ask You for well-being and safety in my religion, my world, my family and my wealth. O Allah, cover my flaws (faults and things that are not appropriate for others to see) and calm me from fear. O Allah, protect me from the front, behind, right, left and above me. I seek refuge in Your greatness, so that I am not snatched from below me (by snakes or swallowed by the earth, etc., which would cause me to fall).	t	Read 1x	The Messenger of Allah, peace and blessings be upon him, never left this supplication in the morning and evening. It contains protection and safety for religion, the world, family, and wealth from various kinds of disturbances that come from all directions.	HR. al-Bukhari in al-Abadul Mufrad No. 1200, Abu Dawud No. 5074, an-Nasa'i VII/282, Ibn Majah No. 3871, al-Hakim 1/517-518, and others from Ibn Umar radhiyallahu 'anhumaa	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
67	Prayer for Seeking Protection from the Whispers of Satan	اَللَّهُمَّ عَالِمَ الْغَيْبِ وَالشَّهَادَةِ فَاطِرَ السَّمَاوَاتِ وَاْلأَرْضِ، رَبَّ كُلِّ شَيْءٍ وَمَلِيْكَهُ، أَشْهَدُ أَنْ لاَ إِلَـهَ إِلاَّ أَنْتَ، أَعُوْذُ بِكَ مِنْ شَرِّ نَفْسِيْ، وَمِنْ شَرِّ الشَّيْطَانِ وَشِرْكِهِ، وَأَنْ أَقْتَرِفَ عَلَى نَفْسِيْ سُوْءًا أَوْ أَجُرَّهُ إِلَى مُسْلِمٍ	allahumma 'aalimal ghoybi wasy-syahaadah faathiros samaawaati wal ardh. robba kulli syai-in wa maliikah. asyhadu alla ilaha illa anta. a'udzu bika min syarri nafsii wa min syarrisy-syaythooni wa syirkihi, wa an aqtarifa 'alaa nafsii suu-an aw ajurrohu ilaa muslim	O Allah, Knower of the unseen and the seen, Creator of the heavens and the earth, Lord of all things and their Sovereign. I bear witness that there is no deity worthy of worship except You. I seek refuge in You from the evil of myself, Satan and his soldiers (temptations to commit shirk against Allah), and I (seek refuge in You) from committing evil against myself or dragging it to a Muslim.	t	Read 1x	The Messenger of Allah, peace and blessings be upon him, said to Abu Bakr as-Siddiq, may Allah be pleased with him, "Say it morning and evening and when you want to sleep."	HR. al-Bukhari in al-Abadul Mufrad No. 1202, at-Tirmidzi No. 3392 and Abu Dawud No. 5067	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
68	Remembrance to Be Protected from All Dangers	بِسْمِ اللَّهِ الَّذِى لاَ يَضُرُّ مَعَ اسْمِهِ شَىْءٌ فِى الأَرْضِ وَلاَ فِى السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ	bismillahilladzi laa yadhurru ma'asmihi syai-un fil ardhi wa laa fis samaa' wa huwas samii'ul 'aliim	In the name of Allah, with whose name nothing in the earth or the heavens can cause harm, and He is the All-Hearing, the All-Knowing.	t	Read 3x	Whoever recites it three times in the morning and evening, nothing will harm him.	HR. at-Tirmidzi No. 3388, Abu Dawud No. 5088, Ibn Majah No. 3869, al-Hakim 1/514, and Ahmad No. 446 and 474	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
69	Declaration of Contentment with Allah, Islam, and the Prophet Muhammad (Peace Be Upon Him)	رَضِيْتُ بِاللهِ رَبًّا، وَبِاْلإِسْلاَمِ دِيْنًا، وَبِمُحَمَّدٍ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ نَبِيًّا	rodhiitu billaahi robbaa wa bil-islaami diinaa, wa bi-muhammadin shallallaahu 'alaihi wa sallama nabiyyaa	I am pleased with Allah as my Lord, Islam as my religion, and Muhammad, peace and blessings be upon him, as my Prophet.	t	Read 3x	Whoever recites it three times in the morning and evening, Allah will grant His pleasure to him on the Day of Resurrection.	HR. Ahmad IV/337, Abu Dawud No. 5072, at-Tirmidzi No. 3389, Ibn Majah No. 3870, an-Nasa'i in 'Amalul Yaum wal Lailah No. 4 and Ibnus Sunni No. 68	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
70	 Asking for Guidance from Allah	يَا حَيُّ يَا قَيُّوْمُ بِرَحْمَتِكَ أَسْتَغِيْثُ، وَأَصْلِحْ لِيْ شَأْنِيْ كُلَّهُ وَلاَ تَكِلْنِيْ إِلَى نَفْسِيْ طَرْفَةَ عَيْنٍ أَبَدًا	yaa hayyu yaa qoyyum, bi-rohmatika as-taghiits, wa ash-lih lii sya'nii kullahu wa laa takilnii ilaa nafsii thorfata 'ainin abadan	O Ever-Living, O Self-Sustaining, by Your mercy I seek help, rectify all my affairs and do not leave me to myself even for the blink of an eye.	t	Read 1x	The meaning of this supplication is that humans are in dire need of Allah and pray that Allah does not abandon them even for a moment.	HR. an-Nasa'i in 'Amalul Yaum wal Lailah No. 575, and al-Hakim 1/545, see Shahiih at-Targhiib wat Tarhiib 1/417 No. 661, Ash-shahiihah No. 227, hasan	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
71	Entering the Evening on the Natural Disposition of Islam	أَمْسَيْنَا عَلَى فِطْرَةِ اْلإِسْلاَمِ وَعَلَى كَلِمَةِ اْلإِخْلاَصِ، وَعَلَى دِيْنِ نَبِيِّنَا مُحَمَّدٍ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ، وَعَلَى مِلَّةِ أَبِيْنَا إِبْرَاهِيْمَ، حَنِيْفًا مُسْلِمًا وَمَا كَانَ مِنَ الْمُشْرِكِيْنَ	amsaynaa 'ala fithrotil islaam wa 'alaa kalimatil ikhlaash, wa 'alaa diini nabiyyinaa Muhammadin shallallahu 'alaihi wa sallam, wa 'alaa millati abiina Ibraahiima haniifam muslimaaw wa maa kaana minal musyrikin	In the evening we are upon the fitrah of Islam, the word of sincerity (the testimony of faith), the religion of our Prophet Muhammad, peace and blessings be upon him, and the religion of our father Abraham, who stood upon the straight path, a Muslim, and was not among the polytheists.	t	Read 1x	'Fitratil Islam' means upon the Sunnah, 'kalimatil ikhlas' means the testimony of faith, and 'hanifan' means a heart inclined towards the straight path and goodness.	HR. Ahmad III/406, 407, ad-Darimi II/292 and Ibnus Sunni in Amalul Yaum wal Lailah No. 34, Misykaatul Mashaabiih No. 2415, Shahiihal-Jaami'ish Shaghiir No. 4674, sahih	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
72	Remembrance of the Oneness of Allah	لاَ إِلَـهَ إِلاَّ اللهُ وَحْدَهُ لاَ شَرِيْكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيْرُ	laa ilaha illallah wahdahu laa syarika lah, lahul mulku walahul hamdu wa huwa 'ala kulli syai-in qodiir	There is no deity worthy of worship except Allah alone, He has no partner. To Him belongs the dominion and all praise. He is over all things competent.	t	Read 1x or 10x in the morning, Read 100x daily	Whoever says this dhikr 100 times a day, it is like freeing 10 slaves, 100 good deeds are recorded for him, 100 mistakes are erased for him, he will be protected from the disturbances of Satan from morning until evening, and no one is better than what he does except someone who practices more than that.	HR al-Bukhari No. 3293 and 6403, Muslim IV/2071 No. 2691 (28), at-Tirmidzi No. 3468, Ibn Majah No. 3798	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
73	Reciting Praise to Allah	سُبْحَانَ اللهِ وَبِحَمْدِهِ عَدَدَ خَلْقَهِ وَرِضَى نَفْسِهِ وَزِنَةَ عَرْشِهِ وَمِدَادَ كَلِمَاتِهِ	subhanallahi wa bihamdihi 'adada khalqihi wa ridha nafsihi wa zinata 'arsyihi wa midada kalimatihi	Glory be to Allah, as many as His creations, Glory be to Allah as much as His pleasure, Glory be to Allah as much as the weight of His Throne, and as much as the ink of His written words.	t	Read 3x	The Prophet, peace and blessings be upon him, told Juwairiyah that the dhikr above has surpassed the dhikr recited by Juwairiyah from after Fajr until Dhuha time.	HR. Muslim No. 2726. Syarah Muslim XVII/44. From Juwairiyah bint al-Harith radhiyallahu 'anha	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
74	Daily Praise (Tasbih and Alhamdulillah)	سُبْحَانَ اللَّهِ وَبِحَمْدِهِ	subhaanallahi wa bihamdihi	Glory be to Allah, and praise be to Him.	t	Read 100x	Whoever says "Subhanallah wa bihamdihi" 100 times in the morning and evening, then nothing will come on the Day of Judgment better than what he has done except one who says the same or more than that.	HR. Muslim No. 2691 and No. 2692, from Abu Hurairah radhiyallahu 'anhu Syarah Muslim XVII/17-18, Shahiih at-Targhiib wat Tarhiib 1/413 No. 653	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
75	Seeking Forgiveness 100 Times a Day	أَسْتَغْفِرُ الله وَأَتُوْبُ إِلَيْهِ	astagh-firullah wa atuubu ilaih	I seek forgiveness from Allah and repent to Him.	t	Read 100x daily	Ibn 'Umar said: The Messenger of Allah, peace and blessings be upon him, said: 'O people, repent to Allah, for indeed I repent to Him one hundred times a day.'	HR. al-Bukhari/Fat-hul Baari XI/101 and Muslim No. 2702	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
76	Prayer for Protection from the Evil of Allah's Creation	أَعُوْذُ بِكَلِمَاتِ اللهِ التَّآمَّاتِ مِنْ شَرِّ مَا خَلَقَ	'audzu bi kalimaatillahittaamaati min syarri ma khalaq	I seek refuge in the perfect words of Allah from the evil of what He has created.	t	Read 3x	Whoever recites it three times in the evening, they will not be afflicted with fever that night.	HR. Ahmad 11/290, an-Nasa'i in 'Amalul Yaum wal Lailah No. 596, Shahiih at-Targhiib wat Tarhiib 1/412 No. 652, Shahiih al-Jaami 'ish Shaghiir No. 6427	f	6	0	0	/static/audio/category_6_Evening_dhikr.mp3
\.


--
-- Data for Name: files; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.files (id, message_id, file_name, file_type, file_size, file_url, uploaded_at) FROM stdin;
\.


--
-- Data for Name: hadith_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hadith_categories (id, name, description, is_active) FROM stdin;
4	Nawawi40	jhajhasjhsaja	t
\.


--
-- Data for Name: hadith_favorites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hadith_favorites (id, hadith_id, user_id, created_at) FROM stdin;
2	14	dd29420b-3be3-4576-ac13-47edc63ab9bb	2025-11-07 12:42:03.038406+00
3	15	dd29420b-3be3-4576-ac13-47edc63ab9bb	2025-11-07 12:42:08.370601+00
\.


--
-- Data for Name: hadith_views; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hadith_views (id, hadith_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: hadiths; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hadiths (id, arabic, translation, narrator, book, number, status, rating, category_id, is_active, featured, view_count, favorite_count) FROM stdin;
15	عَنْ عُمَرَ رَضِيَ اللهُ عَنْهُ أَيْضًا قَالَ: "بَيْنَمَا نَحْنُ جُلُوسٌ عِنْدَ رَسُولِ اللَّهِ صلى الله عليه و سلم ذَاتَ يَوْمٍ، إذْ طَلَعَ عَلَيْنَا رَجُلٌ شَدِيدُ بَيَاضِ الثِّيَابِ، شَدِيدُ سَوَادِ الشَّعْرِ، لَا يُرَى عَلَيْهِ أَثَرُ السَّفَرِ، وَلَا يَعْرِفُهُ مِنَّا أَحَدٌ ... يُعَلِّمُكُمْ دِينَكُمْ".	While we were one day sitting with the Messenger of Allah (ﷺ) there appeared before us a man dressed in extremely white clothes and with very black hair... He said: "That was Jibril. He came to teach you your religion."	Also on the authority of `Umar (ra)	Sahih Muslim	2	Sahih	0	4	t	t	0	0
16	عَنْ أَبِي عَبْدِ الرَّحْمَنِ عَبْدِ اللَّهِ بْنِ عُمَرَ بْنِ الْخَطَّابِ رَضِيَ اللَّهُ عَنْهُمَا قَالَ: سَمِعْتُ رَسُولَ اللَّهِ صلى الله عليه و سلم يَقُولُ: "بُنِيَ الْإِسْلَامُ عَلَى خَمْسٍ: شَهَادَةِ أَنْ لاَ إِلَهَ إِلاَّ اللَّهُ وَأَنَّ مُحَمَّدًا رَسُولُ اللَّهِ، وَإِقَامِ الصَّلاَةِ، وَإِيتَاءِ الزَّكَاةِ، وَالْحَجِّ، وَصَوْمِ رَمَضَانَ".	I heard the Messenger of Allah (ﷺ) say, "Islam has been built on five: testifying that there is no deity worthy of worship except Allah and that Muhammad is the Messenger of Allah, establishing the salah (prayer), paying the zakat (obligatory charity), making the hajj (pilgrimage) to the House, and fasting in Ramadan."	On the authority of Abdullah, the son of Umar ibn al-Khattab (ra)	Sahih al-Bukhari and Sahih Muslim	3	Sahih	0	4	t	f	0	0
17	عَنْ أَبِي عَبْدِ اللَّهِ النُّعْمَانِ بْنِ بَشِيرٍ رَضِيَ اللَّهُ عَنْهُمَا قَالَ: سَمِعْتُ رَسُولَ اللَّهِ صلى الله عليه و سلم يَقُولُ: "إِنَّ الْحَلَالَ بَيِّنٌ وَإِنَّ الْحَرَامَ بَيِّنٌ، وَبَيْنَهُمَا أُمُورٌ مُشْتَبِهَاتٌ لاَ يَعْلَمُهُنَّ كَثِيرٌ مِنَ النَّاسِ... أَلاَ وَإِنَّ فِي الْجَسَدِ مُضْغَةً، إِذَا صَلَحَتْ صَلَحَ الْجَسَدُ كُلُّهُ، وَإِذَا فَسَدَتْ فَسَدَ الْجَسَدُ كُلُّهُ، أَلاَ وَهِيَ الْقَلْبُ".	I heard the Messenger of Allah (ﷺ) say, "That which is lawful is clear and that which is unlawful is clear, and between the two of them are doubtful matters which many people do not know. Thus he who avoids doubtful matters clears himself in regard to his religion and his honor... Truly, it is the heart."	On the authority of an-Nu'man ibn Basheer (ra)	Sahih al-Bukhari and Sahih Muslim	6	Sahih	0	4	t	f	0	0
18	عَنْ أَبِي ذَرٍّ جُنْدَبِ بْنِ جُنَادَةَ، وَأَبِي عَبْدِ الرَّحْمَنِ مُعَاذِ بْنِ جَبَلٍ رَضِيَ اللَّهُ عَنْهُمَا، عَنِ النَّبِيِّ صلى الله عليه و سلم قَالَ: "اتَّقِ اللَّهَ حَيْثُمَا كُنْتَ، وَأَتْبِعِ السَّيِّئَةَ الْحَسَنَةَ تَمْحُهَا، وَخَالِقِ النَّاسَ بِخُلُقٍ حَسَنٍ".	Have taqwa (fear) of Allah wherever you may be, and follow up a bad deed with a good deed which will wipe it out, and behave well towards the people.	On the authority of Abu Dharr Jundub ibn Junadah, and Abu Abdur-Rahman Muadh bin Jabal (may Allah be pleased with him)	Jami at-Tirmidhi	18	Hasan	0	4	t	f	0	0
19	عَنْ عَبْدِ اللَّهِ بْنِ عَبَّاسٍ رَضِيَ اللَّهُ عَنْهُمَا قَالَ: كُنْتُ خَلْفَ النَّبِيِّ صلى الله عليه و سلم يَوْمًا فَقَالَ: "يَا غُلَامُ، إِنِّي أُعَلِّمُكَ كَلِمَاتٍ: احْفَظِ اللَّهَ يَحْفَظْكَ، احْفَظِ اللَّهَ تَجِدْهُ تُجَاهَكَ، إِذَا سَأَلْتَ فَاسْأَلِ اللَّهَ، وَإِذَا اسْتَعَنْتَ فَاسْتَعِنْ بِاللَّهِ... رُفِعَتِ الْأَقْلَامُ وَجَفَّتِ الصُّحُفُ".	One day I was behind the Prophet (peace and blessings of Allah be upon him) when he said to me: "Young man, I shall teach you some words of advice: Be mindful of Allah, and He will protect you; be mindful of Allah, and you will find Him before you... The pens have been lifted and the pages have dried."	On the authority of Abu Abbas Abdullah bin Abbas (may Allah be pleased with him)	Jami at-Tirmidhi	19	Hasan Sahih	0	4	t	f	0	0
14	عَنْ أَمِيرِ الْمُؤْمِنِينَ أَبِي حَفْصٍ عُمَرَ بْنِ الْخَطَّابِ رَضِيَ اللهُ عَنْهُ قَالَ: سَمِعْتُ رَسُولَ اللَّهِ صلى الله عليه وسلم يَقُولُ: " إنَّمَا الْأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى، فَمَنْ كَانَتْ هِجْرَتُهُ إلَى اللَّهِ وَرَسُولِهِ فَهِجْرَتُهُ إلَى اللَّهِ وَرَسُولِهِ، وَمَنْ كَانَتْ هِجْرَتُهُ لِدُنْيَا يُصِيبُهَا أَوْ امْرَأَةٍ يَنْكِحُهَا فَهِجْرَتُهُ إلَى مَا هَاجَرَ إلَيْهِ".	I heard the Messenger of Allah (ﷺ) say: "Actions are (judged) by motives (niyyah), so each man will have what he intended. Thus, he whose migration (hijrah) was to Allah and His Messenger, his migration is to Allah and His Messenger; but he whose migration was for some worldly thing he might gain, or for a wife he might marry, his migration is to that for which he migrated."	It is narrated on the authority of Amirul Mu'minin, Abu Hafs 'Umar bin al-Khattab (ra)	Sahih al-Bukhari and Sahih Muslim	1	Sahih	0	4	t	t	0	0
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.messages (id, conversation_id, sender_type, sender_id, message_text, message_type, file_url, status, created_at) FROM stdin;
\.


--
-- Data for Name: password_reset_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.password_reset_codes (id, user_id, code, expires_at, created_at) FROM stdin;
\.


--
-- Data for Name: ratings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ratings (id, conversation_id, rating, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, username, hashed_password, avatar_url, bio, is_active, is_verified, role, created_at, updated_at, reset_sent_at, latitude, longitude, city, region, country, ip_address, location_accuracy, status) FROM stdin;
dd29420b-3be3-4576-ac13-47edc63ab9bb	users@example.com	Users12345	$2b$12$rU4pKMDSRR1KQd9Bls7.LeH4M5prkKuj1ws9DptD8Nq5fJwL0ziSq	\N	\N	t	f	user	2025-11-01 14:50:49.396676+00	2025-11-05 14:06:18.551783+00	\N	\N	\N	\N	\N	\N	\N	\N	active
2c40bb4c-cf04-45d7-acf3-f228c15aaef6	Ajisafe@example.com	Ajisafe123	$2b$12$uELS.d87lozbQbohvlzT8Oxx5XcHdyciOLkUhRqhb9wAqbjTt8xxy	\N	\N	f	f	user	2025-11-05 12:29:52.12144+00	2025-11-07 17:50:12.383606+00	\N	\N	\N	\N	\N	\N	\N	\N	suspended
7e85cb16-d06d-4026-8db4-199d2364c49d	admin@example.com	Admin123	$2b$12$JtAEZ.jlKPlqN6xPLqIf5urMtCargifWO9G9Xz2Hr6..u0XIHc7dS	\N	\N	t	f	admin	2025-10-29 10:04:14.908485+00	2025-11-03 13:23:53.503865+00	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: zakat_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.zakat_records (id, user_id, name, assets_total, savings, gold_price_per_gram, nisab, zakat_amount, type, note, created_at) FROM stdin;
\.


--
-- Name: allah_names_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.allah_names_id_seq', 99, true);


--
-- Name: bookmarks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bookmarks_id_seq', 1, true);


--
-- Name: contact_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contact_messages_id_seq', 1, false);


--
-- Name: dua_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dua_categories_id_seq', 6, true);


--
-- Name: dua_favorites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dua_favorites_id_seq', 1, false);


--
-- Name: dua_views_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dua_views_id_seq', 1, false);


--
-- Name: duas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.duas_id_seq', 76, true);


--
-- Name: hadith_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.hadith_categories_id_seq', 4, true);


--
-- Name: hadith_favorites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.hadith_favorites_id_seq', 3, true);


--
-- Name: hadith_views_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.hadith_views_id_seq', 1, false);


--
-- Name: hadiths_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.hadiths_id_seq', 19, true);


--
-- Name: password_reset_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.password_reset_codes_id_seq', 1, false);


--
-- Name: zakat_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.zakat_records_id_seq', 1, false);


--
-- Name: admin_notes admin_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_notes
    ADD CONSTRAINT admin_notes_pkey PRIMARY KEY (id);


--
-- Name: admin_users admin_users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_users
    ADD CONSTRAINT admin_users_email_key UNIQUE (email);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: allah_names allah_names_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allah_names
    ADD CONSTRAINT allah_names_pkey PRIMARY KEY (id);


--
-- Name: bookmarks bookmarks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookmarks
    ADD CONSTRAINT bookmarks_pkey PRIMARY KEY (id);


--
-- Name: dua_categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: chat_users chat_users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_users
    ADD CONSTRAINT chat_users_email_key UNIQUE (email);


--
-- Name: chat_users chat_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_users
    ADD CONSTRAINT chat_users_pkey PRIMARY KEY (id);


--
-- Name: contact_messages contact_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact_messages
    ADD CONSTRAINT contact_messages_pkey PRIMARY KEY (id);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: dua_categories dua_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_categories
    ADD CONSTRAINT dua_categories_pkey PRIMARY KEY (id);


--
-- Name: dua_favorites dua_favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_favorites
    ADD CONSTRAINT dua_favorites_pkey PRIMARY KEY (id);


--
-- Name: dua_views dua_views_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_views
    ADD CONSTRAINT dua_views_pkey PRIMARY KEY (id);


--
-- Name: duas duas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.duas
    ADD CONSTRAINT duas_pkey PRIMARY KEY (id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: hadith_categories hadith_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_categories
    ADD CONSTRAINT hadith_categories_name_key UNIQUE (name);


--
-- Name: hadith_categories hadith_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_categories
    ADD CONSTRAINT hadith_categories_pkey PRIMARY KEY (id);


--
-- Name: hadith_favorites hadith_favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_favorites
    ADD CONSTRAINT hadith_favorites_pkey PRIMARY KEY (id);


--
-- Name: hadith_views hadith_views_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_views
    ADD CONSTRAINT hadith_views_pkey PRIMARY KEY (id);


--
-- Name: hadiths hadiths_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadiths
    ADD CONSTRAINT hadiths_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: password_reset_codes password_reset_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_codes
    ADD CONSTRAINT password_reset_codes_pkey PRIMARY KEY (id);


--
-- Name: ratings ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_pkey PRIMARY KEY (id);


--
-- Name: dua_favorites uq_dua_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_favorites
    ADD CONSTRAINT uq_dua_user UNIQUE (dua_id, user_id);


--
-- Name: hadith_favorites uq_hadith_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_favorites
    ADD CONSTRAINT uq_hadith_user UNIQUE (hadith_id, user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: zakat_records zakat_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zakat_records
    ADD CONSTRAINT zakat_records_pkey PRIMARY KEY (id);


--
-- Name: ix_allah_names_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_allah_names_id ON public.allah_names USING btree (id);


--
-- Name: ix_bookmarks_ayah_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bookmarks_ayah_key ON public.bookmarks USING btree (ayah_key);


--
-- Name: ix_bookmarks_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bookmarks_id ON public.bookmarks USING btree (id);


--
-- Name: ix_categories_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_categories_id ON public.dua_categories USING btree (id);


--
-- Name: ix_contact_messages_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_contact_messages_id ON public.contact_messages USING btree (id);


--
-- Name: ix_duas_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_duas_id ON public.duas USING btree (id);


--
-- Name: ix_duas_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_duas_title ON public.duas USING btree (title);


--
-- Name: ix_hadith_categories_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_hadith_categories_id ON public.hadith_categories USING btree (id);


--
-- Name: ix_hadiths_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_hadiths_id ON public.hadiths USING btree (id);


--
-- Name: ix_password_reset_codes_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_reset_codes_code ON public.password_reset_codes USING btree (code);


--
-- Name: ix_password_reset_codes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_reset_codes_id ON public.password_reset_codes USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_zakat_records_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zakat_records_id ON public.zakat_records USING btree (id);


--
-- Name: ix_zakat_records_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zakat_records_user_id ON public.zakat_records USING btree (user_id);


--
-- Name: admin_notes admin_notes_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_notes
    ADD CONSTRAINT admin_notes_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.admin_users(id);


--
-- Name: admin_notes admin_notes_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_notes
    ADD CONSTRAINT admin_notes_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id);


--
-- Name: bookmarks bookmarks_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookmarks
    ADD CONSTRAINT bookmarks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: conversations conversations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: dua_favorites dua_favorites_dua_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_favorites
    ADD CONSTRAINT dua_favorites_dua_id_fkey FOREIGN KEY (dua_id) REFERENCES public.duas(id) ON DELETE CASCADE;


--
-- Name: dua_favorites dua_favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_favorites
    ADD CONSTRAINT dua_favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: dua_views dua_views_dua_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_views
    ADD CONSTRAINT dua_views_dua_id_fkey FOREIGN KEY (dua_id) REFERENCES public.duas(id) ON DELETE CASCADE;


--
-- Name: dua_views dua_views_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dua_views
    ADD CONSTRAINT dua_views_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: duas duas_dua_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.duas
    ADD CONSTRAINT duas_dua_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.dua_categories(id) ON DELETE SET NULL;


--
-- Name: files files_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.messages(id);


--
-- Name: bookmarks fk_bookmarks_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookmarks
    ADD CONSTRAINT fk_bookmarks_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: hadith_favorites hadith_favorites_hadith_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_favorites
    ADD CONSTRAINT hadith_favorites_hadith_id_fkey FOREIGN KEY (hadith_id) REFERENCES public.hadiths(id) ON DELETE CASCADE;


--
-- Name: hadith_favorites hadith_favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_favorites
    ADD CONSTRAINT hadith_favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: hadith_views hadith_views_hadith_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_views
    ADD CONSTRAINT hadith_views_hadith_id_fkey FOREIGN KEY (hadith_id) REFERENCES public.hadiths(id) ON DELETE CASCADE;


--
-- Name: hadith_views hadith_views_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadith_views
    ADD CONSTRAINT hadith_views_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: hadiths hadiths_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hadiths
    ADD CONSTRAINT hadiths_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.hadith_categories(id) ON DELETE SET NULL;


--
-- Name: messages messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id);


--
-- Name: password_reset_codes password_reset_codes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_codes
    ADD CONSTRAINT password_reset_codes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: ratings ratings_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict flJXfROPitwcx6X9Crwqageuj7GdPE5f0UUaUv4gSfIGTBWH9tw1JkWQv3oyV4I

