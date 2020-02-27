from pprint import pprint
from glob import glob
from typing import Dict, List, Union, Tuple, Optional
import regex as re
import os.path as op
from cltk.tokenize.word import WordTokenizer
from lxml.builder import E as Builder
import lxml.etree as ET

from helpers.reader.capitains import transform
from MyCapytain.common.constants import Mimetypes
from MyCapytain.common.utils import parse
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText, CapitainsCtsPassage

LANG = "lat"
RAISE_ON_NO_CITATION = True
PATH_TSV = "./data/curated/corpus/base"
XML_FILES = "./data/raw/corpora/**/*.xml"

n_exceptions = []

# an exceptions for -n from Collatinus Data
n_exceptions += ['Acarnan', 'Aegipan', 'Alcman', 'Aman', 'Azan', 'Balaan', 'Balanan', 'Cainan', 'Chanaan', 'Chanan',
                 'Euan', 'Euhan', 'Joathan', 'Johanan', 'Laban', 'Leviathan', 'Madian', 'Magedan', 'Naaman',
                 'Nabuzardan', 'Nathan', 'Nisan', 'Pan', 'Pharan', 'Satan', 'Titan', 'dan', 'forsan', 'forsitan',
                 'fortan', 'fortassean', 'man', 'paean', 'tragopan']
# en exceptions for -n from Collatinus Data
n_exceptions += ['Astarthen', 'Bethaven', 'Cebren', 'Cophen', 'Damen', 'Eden', 'Hellen', 'Manahen', 'Philopoemen',
                 'Ruben', 'Siren', 'Troezen', 'Tychen', 'Zosimen', 'abdomen', 'abdumen', 'absegmen', 'acumen',
                 'adaugmen', 'adfamen', 'adflamen', 'adhortamen', 'adjuvamen', 'adligamen', 'adnomen', 'aequamen',
                 'aeramen', 'agmen', 'agnomen', 'albamen', 'albumen', 'almen', 'alumen', 'amen', 'amicimen', 'anguen',
                 'arcumen', 'argyranchen', 'arsen', 'aspectamen', 'aspiramen', 'attagen', 'aucupiamen', 'augmen',
                 'bitumen', 'cacumen', 'caelamen', 'calceamen', 'calciamen', 'cantamen', 'carmen', 'catillamen',
                 'cavamen', 'certamen', 'chalasticamen', 'cicuticen', 'circen', 'citharicen', 'clinamen', 'cluden',
                 'cogitamen', 'cognomen', 'columen', 'conamen', 'consolamen', 'contamen', 'conttamen', 'cornicen',
                 'coronamen', 'coruscamen', 'crassamen', 'creamen', 'crimen', 'cruciamen', 'culmen', 'cunctamen',
                 'curmen', 'curvamen', 'cyclamen', 'decoramen', 'detramen', 'dictamen', 'discrimen', 'docimen',
                 'documen', 'dolamen', 'donamen', 'dulceamen', 'duramen', 'ebriamen', 'effamen', 'eliquamen',
                 'epinomen', 'examen', 'excusamen', 'exhortamen', 'famen', 'farcimen', 'femen', 'ferrumen', 'ferumen',
                 'fidamen', 'fidicen', 'figmen', 'filamen', 'firmamen', 'flamen', 'flemen', 'flumen', 'foramen',
                 'formidamen', 'fragmen', 'frumen', 'frustramen', 'fulcimen', 'fulmen', 'fundamen', 'generamen',
                 'genimen', 'germen', 'gestamen', 'glomeramen', 'gluten', 'gramen', 'gravamen', 'gubernamen', 'gumen',
                 'hortamen', 'hymen', 'hyphen', 'imitamen', 'inchoamen', 'inflamen', 'inguen', 'inspiramen',
                 'intercisimen', 'involumen', 'irritamen', 'juvamen', 'laetamen', 'lassamen', 'lateramen', 'legumen',
                 'lenimen', 'levamen', 'libamen', 'libramen', 'lichen', 'lien', 'ligamen', 'lignamen', 'limen',
                 'linamen', 'linimen', 'linteamen', 'liquamen', 'litamen', 'liticen', 'luctamen', 'lumen', 'lustramen',
                 'lyricen', 'machinamen', 'manamen', 'medicamen', 'meditamen', 'miseramen', 'moderamen', 'modulamen',
                 'molimen', 'momen', 'motamen', 'munimen', 'nemen', 'nodamen', 'nomen', 'notamen', 'novamen',
                 'nullificamen', 'numen', 'nutamen', 'nutrimen', 'objectamen', 'oblectamen', 'oblenimen', 'occamen',
                 'odoramen', 'oleamen', 'omen', 'ornamen', 'oscen', 'osmen', 'ostentamen', 'palpamen', 'peccamen',
                 'pecten', 'pedamen', 'perflamen', 'petimen', 'piamen', 'pilumen', 'pinguamen', 'placamen', 'polimen',
                 'pollen', 'postlimen', 'praecantamen', 'praeexercitamen', 'praefamen', 'praeligamen', 'praenomen',
                 'praesegmen', 'precamen', 'proflamen', 'prolimen', 'pronomen', 'propagmen', 'psalmicen', 'pullamen',
                 'pulpamen', 'purgamen', 'putamen', 'putramen', 'pyren', 'rasamen', 'refluamen', 'regimen', 'relevamen',
                 'religamen', 'remoramen', 'ren', 'renovamen', 'resegmen', 'respiramen', 'revocamen', 'rogamen',
                 'ructamen', 'rumen', 'saepimen', 'sagmen', 'salsamen', 'sanguen', 'sarcimen', 'sarmen', 'saturamen',
                 'sedamen', 'sedimen', 'segmen', 'semen', 'sepimen', 'signamen', 'simulamen', 'sinuamen', 'siticen',
                 'solamen', 'solen', 'solidamen', 'specimen', 'spectamen', 'speculamen', 'spiramen', 'splen',
                 'spurcamen', 'sputamen', 'stabilimen', 'stamen', 'statumen', 'stipamen', 'stramen', 'sublimen',
                 'substamen', 'substramen', 'subtegmen', 'suffimen', 'sufflamen', 'sulcamen', 'sumen', 'superlimen',
                 'susurramen', 'synanchen', 'tamen', 'tegimen', 'tegmen', 'tegumen', 'temptamen', 'tentamen',
                 'terebramen', 'termen', 'testamen', 'tibicen', 'tormen', 'tramen', 'tubicen', 'tumulamen', 'turben',
                 'tutamen', 'ululamen', 'unguen', 'vegetamen', 'velamen', 'velumen', 'verumtamen', 'veruntamen',
                 'vexamen', 'vibramen', 'vimen', 'vitreamen', 'vitulamen', 'vocamen', 'volumen']
# in exceptions for -n from Collatinus Data
n_exceptions += ['Arin', 'Attin', 'Benjamin', 'Cain', 'Corozain', 'Dothain', 'Eleusin', 'Eliacin', 'Engonasin',
                 'Joachin', 'Seraphin', 'Trachin', 'Tubalcain', 'ain', 'alioquin', 'atquin', 'ceteroquin', 'cherubin',
                 'delfin', 'delphin', 'hin', 'nostin', 'quin', 'satin', 'sin']
# on exceptions for -n from Collatinus Data
n_exceptions += ['Aaron', 'Abaddon', 'Abessalon', 'Abiron', 'Absalon', 'Accaron', 'Acheron', 'Achilleon', 'Acmon',
                 'Acroathon', 'Actaeon', 'Adipson', 'Adon', 'Aeantion', 'Aegaeon', 'Aegilion', 'Aegion', 'Aegon',
                 'Aemon', 'Aeson', 'Aethion', 'Aethon', 'Aetion', 'Agamemnon', 'Aglaophon', 'Ajalon', 'Alabastron',
                 'Alabon', 'Albion', 'Alcimedon', 'Alcmaeon', 'Alcon', 'Alcumaeon', 'Alcyon', 'Alebion', 'Alemon',
                 'Alexion', 'Aliacmon', 'Alison', 'Almon', 'Alymon', 'Amazon', 'Amithaon', 'Amithhaon', 'Ammon',
                 'Amnon', 'Amorion', 'Amphictyon', 'Amphimedon', 'Amphion', 'Amphitryon', 'Amydon', 'Amythaon',
                 'Amyzon', 'Anacreon', 'Anaon', 'Andraemon', 'Andremon', 'Androgeon', 'Androtion', 'Anticyricon',
                 'Antiphon', 'Antron', 'Aon', 'Apion', 'Apollyon', 'Apteron', 'Arethon', 'Arion', 'Aristocreon',
                 'Aristogiton', 'Ariston', 'Aristophon', 'Artacaeon', 'Arthedon', 'Asarhaddon', 'Asidon', 'Aspledon',
                 'Astragon', 'Astron', 'Aulion', 'Auson', 'Automedon', 'Auximon', 'Avenion', 'Axion', 'Babylon',
                 'Baeton', 'Barcinon', 'Batton', 'Bellerophon', 'Bethoron', 'Bion', 'Bithynion', 'Biton', 'Blascon',
                 'Blepharon', 'Borion', 'Branchiadon', 'Brauron', 'Bronton', 'Bruchion', 'Bryalion', 'Bryazon',
                 'Bryllion', 'Bubon', 'Bucion', 'Byzantion', 'Cacomnemon', 'Calcedon', 'Calchedon', 'Calliphon',
                 'Callon', 'Calon', 'Calydon', 'Carchedon', 'Carnion', 'Caulon', 'Cedron', 'Celadon', 'Cerberion',
                 'Cercyon', 'Ceron', 'Chaeremon', 'Chalaeon', 'Chalcedon', 'Chaon', 'Chardaleon', 'Charon', 'Cheraemon',
                 'Chersiphron', 'Chilon', 'Chimerion', 'Chion', 'Chiron', 'Choerogylion', 'Cimon', 'Cisamon',
                 'Cithaeron', 'Citheron', 'Claeon', 'Cleomedon', 'Cleon', 'Cleophon', 'Codrion', 'Colophon', 'Condylon',
                 'Conon', 'Corragon', 'Corrhagon', 'Corydon', 'Cothon', 'Cotton', 'Cotyaion', 'Crannon', 'Cranon',
                 'Cremmyon', 'Creon', 'Crialoon', 'Criumetopon', 'Cromyon', 'Ctesiphon', 'Cydon', 'Daedalion', 'Dagon',
                 'Daiphron', 'Dalion', 'Damasichthon', 'Damon', 'Dareion', 'Deltoton', 'Demetrion', 'Demoleon',
                 'Demophon', 'Demophoon', 'Deucalion', 'Dexon', 'Diaron', 'Didumaon', 'Didymaon', 'Didymeon',
                 'Dindymon', 'Dinon', 'Diomedon', 'Dion', 'Diptychon', 'Dipylon', 'Dolichaon', 'Dolon', 'Dorion',
                 'Doriscon', 'Dortigon', 'Dotion', 'Dracanon', 'Edon', 'Eetion', 'Eion', 'Electruon', 'Electryon',
                 'Eluron', 'Emathion', 'Endymion', 'Enguion', 'Engyon', 'Eon', 'Ephron', 'Erineon', 'Erisichthon',
                 'Erotopaegnion', 'Erysichthon', 'Esdrelon', 'Euagon', 'Euctemon', 'Eudaemon', 'Eudon', 'Euphorion',
                 'Euphron', 'Euprosopon', 'Eurymedon', 'Eurytion', 'Gabaon', 'Gargaron', 'Gedeon', 'Gehon', 'Gelon',
                 'Genethliacon', 'Geon', 'Georgicon', 'Gerrhon', 'Gerson', 'Geryon', 'Glycon', 'Gorgon', 'Gyrton',
                 'Habron', 'Haemon', 'Hagnon', 'Haliacmon', 'Hammon', 'Hannon', 'Harmedon', 'Harpocration', 'Hebon',
                 'Hebron', 'Helicaon', 'Helicon', 'Hephaestion', 'Hermacreon', 'Hesebon', 'Hexaemeron', 'Hexapylon',
                 'Hicetaon', 'Hieron', 'Hilarion', 'Hippocoon', 'Hippomedon', 'Hippon', 'Holmon', 'Holon', 'Hygienon',
                 'Hypaton', 'Hyperion', 'Iasion', 'Icadion', 'Icosion', 'Idmon', 'Ilion', 'Imaon', 'Iseon', 'Ixion',
                 'Jason', 'Lacedaemon', 'Lacon', 'Lacydon', 'Ladon', 'Laestrygon', 'Lagon', 'Lampon', 'Laocoon',
                 'Laomedon', 'Laucoon', 'Lauron', 'Lecton', 'Leocorion', 'Leon', 'Lepreon', 'Leprion', 'Lestrygon',
                 'Lethon', 'Lilybaeon', 'Lycaon', 'Lycon', 'Lycophon', 'Lycophron', 'Lydion', 'Lyson', 'Macedon',
                 'Machaon', 'Maeon', 'Maeson', 'Mageddon', 'Magon', 'Marathon', 'Marcion', 'Mathon', 'Medeon', 'Medon',
                 'Memnon', 'Menephron', 'Menon', 'Mentonomon', 'Metagon', 'Methion', 'Metion', 'Meton', 'Micon',
                 'Miction', 'Micton', 'Milanion', 'Milon', 'Mirsion', 'Mision', 'Mnason', 'Mnemon', 'Mnesigiton',
                 'Molon', 'Mulon', 'Mycon', 'Mydon', 'Mygdon', 'Myrmidon', 'Naasson', 'Nahasson', 'Naron', 'Narycion',
                 'Nasamon', 'Nebon', 'Neon', 'Nicephorion', 'Nicon', 'Noemon', 'Nomion', 'Oenopion', 'Olizon', 'Ophion',
                 'Orchomenon', 'Orion', 'Oromedon', 'Ortiagon', 'Paeon', 'Palaemon', 'Pallon', 'Pandion', 'Panopion',
                 'Pantaleon', 'Pantheon', 'Paphlagon', 'Paridon', 'Parion', 'Parmenion', 'Parthaon', 'Parthenion',
                 'Parthenon', 'Passaron', 'Patron', 'Paulon', 'Pedon', 'Pelagon', 'Pelion', 'Pellaon', 'Pergamon',
                 'Peteon', 'Phaedon', 'Phaenon', 'Phaethon', 'Phalerion', 'Phaleron', 'Phaon', 'Pharaon', 'Pharathon',
                 'Phidon', 'Philammon', 'Philemon', 'Philistion', 'Philon', 'Phison', 'Phlegethon', 'Phlegon',
                 'Phocion', 'Phradmon', 'Phryxelon', 'Physcon', 'Pion', 'Pitholeon', 'Pleuron', 'Pluton', 'Polemon',
                 'Polydaemon', 'Polygiton', 'Polypemon', 'Polyperchon', 'Porphyrion', 'Prion', 'Procyon', 'Protagorion',
                 'Protheon', 'Pseudostomon', 'Pteleon', 'Pygmalion', 'Pyracmon', 'Pyriphlegethon', 'Python', 'Region',
                 'Rhinthon', 'Rhinton', 'Rhion', 'Rhizon', 'Rhoetion', 'Rhytion', 'Rubicon', 'Rumon', 'Salomon',
                 'Samson', 'Sarion', 'Sarpedon', 'Sason', 'Satiricon', 'Satyricon', 'Sciron', 'Scyron', 'Sebeon',
                 'Sicyon', 'Sidon', 'Sigalion', 'Silaniion', 'Silanion', 'Simeon', 'Simon', 'Sinon', 'Sisichthon',
                 'Sisichton', 'Sithon', 'Socration', 'Solomon', 'Solon', 'Sophron', 'Spiridion', 'Stilbon', 'Stilpon',
                 'Stimichon', 'Stimon', 'Stratioton', 'Straton', 'Strenion', 'Strongylion', 'Strymon', 'Sunion',
                 'Taenaron', 'Tarracon', 'Tauron', 'Taygeton', 'Technopaegnion', 'Tecmon', 'Telamon', 'Telon',
                 'Tenthredon', 'Teredon', 'Teuthredon', 'Thabusion', 'Thelbon', 'Themison', 'Theon', 'Thermodon',
                 'Theromedon', 'Theron', 'Thesbon', 'Thronion', 'Thryon', 'Thylon', 'Timoleon', 'Timon', 'Topazion',
                 'Topazon', 'Trallicon', 'Trevidon', 'Triton', 'Tritonon', 'Tryphon', 'Tylon', 'Typhon', 'Ucalegon',
                 'Vibon', 'Vulchalion', 'Xenophon', 'Zabulon', 'Zenon', 'Zephyrion', 'Zon', 'Zopyrion', 'acanthion',
                 'aconiton', 'acopon', 'acoron', 'acratophoron', 'acrochordon', 'acrocolion', 'acron', 'adamenon',
                 'adipsatheon', 'aedon', 'aegolethron', 'aeon', 'aesalon', 'aeschrion', 'agaricon', 'agathodaemon',
                 'ageraton', 'agon', 'agriophyllon', 'aizoon', 'alazon', 'alexipharmacon', 'allasson', 'alphiton',
                 'alypon', 'alyseidion', 'alysidion', 'alysson', 'alyssson', 'amaracion', 'amerimnon', 'amethystizon',
                 'ammonitron', 'amomon', 'ampeloprason', 'amphibion', 'anabibazon', 'anacoluthon', 'anagon',
                 'anarrhinon', 'ancistron', 'ancon', 'ancyloblepharon', 'andron', 'androsaemon', 'annon', 'anodynon',
                 'anteridion', 'anthedon', 'anthereon', 'anthyllion', 'antibiblion', 'antipharmacon', 'antirrhinon',
                 'antiscorodon', 'antistrephon', 'antitheton', 'antizeugmenon', 'aphron', 'apiacon', 'apocynon',
                 'apographon', 'apologeticon', 'apoproegmenon', 'aposcopeuon', 'arcebion', 'archebion', 'archidiacon',
                 'archigeron', 'architecton', 'archon', 'arcion', 'arcoleon', 'arction', 'argemon', 'argemonion',
                 'argennon', 'aristereon', 'armon', 'arnion', 'arnoglosson', 'aron', 'arrhenogonon', 'arsenogonon',
                 'artemedion', 'artemon', 'arusion', 'asaron', 'asbeston', 'ascalon', 'asceterion', 'asclepion',
                 'ascyron', 'asphaltion', 'aspideion', 'asplenon', 'asterion', 'astrabicon', 'astrion', 'asyndeton',
                 'asyntrophon', 'athenogeron', 'athlon', 'atlantion', 'aulon', 'autochthon', 'autochton', 'automaton',
                 'axon', 'azymon', 'barbiton', 'barypicron', 'barython', 'basilicon', 'batrachion', 'bechion', 'belion',
                 'bisdiapason', 'bison', 'blachnon', 'blechhnon', 'blechon', 'blechron', 'bolbiton', 'botryon',
                 'boustrophedon', 'brochon', 'bryon', 'bubalion', 'bubonion', 'buleuterion', 'bunion', 'bupleuron',
                 'burrhinon', 'buselinon', 'bustrophedon', 'busycon', 'butyron', 'caballion', 'cacemphaton',
                 'cacodaemon', 'cacophaton', 'cacosyntheton', 'cacozelon', 'caesapon', 'calligonon', 'callion',
                 'callipetalon', 'callitrichon', 'calopodion', 'camelopodion', 'cammaron', 'canon', 'carcinethron',
                 'carcinothron', 'carpophyllon', 'caryllon', 'caryon', 'caryophyllon', 'caryphyllon', 'cassiteron',
                 'catalepton', 'causon', 'centaurion', 'cephalaeon', 'ceration', 'cerion', 'cestron', 'chaerephyllon',
                 'chalazion', 'chalcanthon', 'chalcanton', 'chamaedracon', 'chamaeleon', 'chamaemelon', 'chamaezelon',
                 'charisticon', 'charistion', 'chariton', 'charitonblepharon', 'chelidon', 'chelyon', 'chenoboscion',
                 'chiliophyllon', 'chirographon', 'chironomon', 'chlorion', 'chondrillon', 'chreston', 'chrysallion',
                 'chrysanthemon', 'cichorion', 'cinnamon', 'circaeon', 'cirsion', 'cissaron', 'cission', 'cleonicion',
                 'cleopiceton', 'clidion', 'clinopodion', 'cneoron', 'cnestron', 'coacon', 'cobion', 'coenon',
                 'colobathron', 'colon', 'comaron', 'contomonobolon', 'coriandron', 'corion', 'corisson', 'corymbion',
                 'cotyledon', 'crataegon', 'crataeogonon', 'crinon', 'crocodileon', 'crocodilion', 'croton',
                 'crysallion', 'crystallion', 'cuferion', 'cybion', 'cyceon', 'cyclaminon', 'cylon', 'cymation',
                 'cynocardamon', 'cynocephalion', 'cynodon', 'cynomazon', 'cynomorion', 'cynorrhodon', 'cynorrodon',
                 'cynozolon', 'cyperon', 'daemon', 'daimon', 'damasonion', 'daphnon', 'daucion', 'daucon', 'deleterion',
                 'diaartymaton', 'diabotanon', 'diacerason', 'diacheton', 'diachyton', 'diacochlecon', 'diacodion',
                 'diacon', 'diaglaucion', 'diagrydion', 'dialibanon', 'dialion', 'dialthaeon', 'dialyton',
                 'diameliloton', 'diameliton', 'diamoron', 'diapanton', 'diapason', 'diaprasion', 'diascorodon',
                 'diasmyrnon', 'diaspermaton', 'diatessaron', 'diatoichon', 'diatonicon', 'diazeugmenon', 'dichalcon',
                 'dichomenion', 'diezeugmenon', 'digammon', 'diospyron', 'dircion', 'disdiapason', 'distichon',
                 'dodecatemorion', 'dodecatheon', 'dorcadion', 'dorcidion', 'doron', 'dorycnion', 'dorypetron',
                 'dracon', 'dracontion', 'dryophonon', 'dysprophoron', 'ebenotrichon', 'echeon', 'echion', 'ectomon',
                 'egersimon', 'elaeon', 'elaphoboscon', 'elegeion', 'elegeon', 'elegidarion', 'elegidion', 'elegion',
                 'eleison', 'embadon', 'emmoton', 'emplecton', 'enchiridion', 'enemion', 'engonaton', 'enhaemon',
                 'enneaphyllon', 'epagon', 'ephedron', 'ephemeron', 'epicedion', 'epigrammation', 'epimedion',
                 'epinicion', 'epipetron', 'epiradion', 'epitaphion', 'epithalamion', 'epitheton', 'epithymon',
                 'epitonion', 'epomphalion', 'eranthemon', 'erigeron', 'erioxylon', 'eryngion', 'erysisceptron',
                 'erythraicon', 'erythranon', 'eschatocollion', 'etymon', 'eubolion', 'eucharisticon', 'eugalacton',
                 'eunuchion', 'euphrosynon', 'eupteron', 'eutheriston', 'euzomon', 'exacon', 'exonychon', 'exormiston',
                 'galeobdolon', 'galion', 'gamelion', 'ganglion', 'garyophyllon', 'geranion', 'gethyon', 'gingidion',
                 'glaucion', 'glechon', 'glinon', 'glycyrrhizon', 'gnaphalion', 'gnomon', 'gossipion', 'gossypion',
                 'hadrobolon', 'haematicon', 'halcyon', 'halicacabon', 'halimon', 'halipleumon', 'halmyridion', 'halon',
                 'hecatombion', 'hegemon', 'hegemonicon', 'heleoselinon', 'heliochryson', 'helioscopion',
                 'helioselinon', 'heliotropion', 'hemerobion', 'hemionion', 'hemisphaerion', 'hemitonion', 'hepatizon',
                 'heptaphyllon', 'heroion', 'heterocliton', 'hexaclinon', 'hexaphoron', 'hieracion', 'hieromnemon',
                 'hippolapathon', 'hippomarathon', 'hippophaeston', 'hippopheon', 'hippophlomon', 'hipposelinon',
                 'histon', 'hodoeporicon', 'holocyron', 'holosteon', 'homoeopropheron', 'homoeoprophoron',
                 'homoeoptoton', 'homoeoteleuton', 'horaeon', 'horizon', 'hormiscion', 'hyacinthizon', 'hydrogeron',
                 'hydrolapathon', 'hypecoon', 'hyperbaton', 'hypericon', 'hypocauston', 'hypogeson', 'hypoglottion',
                 'hypomochlion', 'hypopodion', 'ichneumon', 'icon', 'idolon', 'ion', 'iphyon', 'ischaemon',
                 'isocinnamon', 'isopleuron', 'isopyron', 'langon', 'larbason', 'ledon', 'leontocaron', 'leontopetalon',
                 'leontopodion', 'leptophyllon', 'leucanthemon', 'leuceoron', 'leucoion', 'leucon', 'leucophoron',
                 'leucrion', 'leuson', 'lexidion', 'libadion', 'lignyzon', 'limodoron', 'limonion', 'linostrophon',
                 'lirinon', 'lirion', 'lithizon', 'lithognomon', 'lithospermon', 'logarion', 'longanon', 'lucmon',
                 'lychnion', 'lyncurion', 'lyron', 'lytron', 'machaerophyllon', 'madon', 'maldacon', 'malobathron',
                 'mammon', 'manicon', 'manon', 'margarition', 'maron', 'maronion', 'mastichelaeon', 'mazonomon',
                 'mecon', 'meconion', 'medion', 'melamphyllon', 'melampodion', 'melanspermon', 'melanthion',
                 'melaspermon', 'melissophyllon', 'meliton', 'melocarpon', 'melophyllon', 'melothron', 'memecylon',
                 'menion', 'menogenion', 'mesanculon', 'metopion', 'metopon', 'metron', 'mileon', 'miuron',
                 'mnemosynon', 'monazon', 'monemeron', 'monobolon', 'monochordon', 'monosyllabon', 'morion',
                 'mormorion', 'myacanthon', 'myophonon', 'myosoton', 'myriophyllon', 'myrmecion', 'myron',
                 'myrtopetalon', 'mystron', 'myxarion', 'myxon', 'nardostachyon', 'naulon', 'nechon', 'necnon',
                 'nephelion', 'nerion', 'nession', 'neurospaston', 'nicephyllon', 'nitrion', 'non', 'notion',
                 'nyctegreton', 'nymphon', 'nysion', 'octaphhoron', 'octaphoron', 'octophoron', 'ololygon',
                 'onocardion', 'onochelon', 'onochilon', 'onopordon', 'onopradon', 'ophidion', 'ophiostaphylon',
                 'opion', 'opition', 'opocarpathon', 'orchion', 'oreon', 'oreoselinon', 'orestion', 'origanon',
                 'ornithon', 'orobethron', 'otion', 'oxybaphon', 'oxylapathon', 'oxytonon', 'oxytriphyllon',
                 'panathenaicon', 'pancration', 'panion', 'paradoxon', 'paranarrhinon', 'paranatellon', 'parelion',
                 'pareoron', 'parergon', 'parhelion', 'parhomoeon', 'parison', 'paromoeon', 'paronymon', 'parthenicon',
                 'pausilypon', 'pedalion', 'peganon', 'pelecinon', 'pellion', 'pentadactylon', 'pentagonon',
                 'pentaphyllon', 'pentaspaston', 'pentatomon', 'pentorobon', 'perichristarion', 'perinaeon', 'perineon',
                 'periosteon', 'peripodion', 'perispomenon', 'perisson', 'peristereon', 'petroselinon', 'peucedanon',
                 'phaenion', 'phaenomenon', 'phalaecion', 'phalangion', 'pharicon', 'pharnaceon', 'pharnacion',
                 'phasganion', 'phellandrion', 'pheuxaspidion', 'philanthropion', 'phlegmon', 'phorimon', 'phrenion',
                 'phryganion', 'phrynion', 'phyllon', 'phynon', 'physiognomon', 'pisselaeon', 'pitydion', 'pityon',
                 'platanon', 'platon', 'platyphyllon', 'plethron', 'polion', 'polyandrion', 'polyarchion', 'polyarcyon',
                 'polycnemon', 'polygonaton', 'polyneuron', 'polypodion', 'polyptoton', 'polyrrhizon', 'polyrrizon',
                 'polyspaston', 'polysyntheton', 'polytrichon', 'poppyzon', 'potamogeton', 'potamogiton', 'poterion',
                 'pramnion', 'prapedilon', 'prapedion', 'prasion', 'prason', 'proarchon', 'probation', 'procoeton',
                 'procomion', 'proegmenon', 'prognosticon', 'promnion', 'pronaon', 'propempticon', 'propnigeon',
                 'propylaeon', 'propylon', 'prosopon', 'protagion', 'protrepticon', 'protropon', 'pseudobunion',
                 'pseudoselinon', 'psychotrophon', 'psyllion', 'pteron', 'pycnocomon', 'pyrethron', 'pythion',
                 'pythonion', 'quilon', 'rhagion', 'rhapeion', 'rhaphanidion', 'rhigolethron', 'rhinion',
                 'rhododendron', 'rhopalon', 'rhuselinon', 'rhythmizomenon', 'saccharon', 'sacon', 'sagapenon',
                 'sagenon', 'sanchromaton', 'sangenon', 'saphon', 'sarcion', 'satyrion', 'saurion', 'scazon',
                 'scimpodion', 'sciothericon', 'scolecion', 'scolibrochon', 'scolopendrion', 'scordilon', 'scordion',
                 'scorodon', 'scorpioctonon', 'scorpion', 'scorpiuron', 'scybalon', 'selenion', 'selenogonon',
                 'selinon', 'selinophyllon', 'semimetopion', 'semnion', 'sepioticon', 'serapion', 'setanion',
                 'sicelicon', 'siderion', 'sindon', 'sion', 'siphon', 'sisonagrion', 'sisyrinchion', 'sisyringion',
                 'smilion', 'smyrnion', 'sophismation', 'sparganion', 'sparton', 'spathalion', 'sphaerion', 'sphingion',
                 'sphondylion', 'splenion', 'spondiazon', 'spondylion', 'stacton', 'staphylodendron', 'stasimon',
                 'statioron', 'stergethron', 'stomation', 'stratopedon', 'struthion', 'subdiacon', 'sycaminon',
                 'sycophyllon', 'symphyton', 'symposion', 'syndon', 'synemmenon', 'syngenicon', 'synoneton',
                 'synonymon', 'syntonon', 'syntononon', 'syreon', 'syron', 'taurophthalmon', 'technyphion', 'telephion',
                 'tenon', 'teramon', 'tetartemorion', 'tethalassomenon', 'tetrachordon', 'tetracolon', 'tetragnathion',
                 'tetraptoton', 'tetrastichon', 'tetrastylon', 'teucrion', 'teuthrion', 'theatridion', 'thelycon',
                 'thelygonon', 'thelyphonon', 'theobrotion', 'theodotion', 'theoremation', 'theribethron', 'therion',
                 'theriophonon', 'thermospodion', 'thesion', 'thorybethron', 'thorybetron', 'thrauston', 'thrion',
                 'thymion', 'thyon', 'tiphyon', 'tithymalon', 'tordylion', 'tordylon', 'toxicon', 'tragion',
                 'tragopogon', 'trapezophoron', 'tribon', 'trichalcon', 'tricolon', 'trigon', 'trihemitonion',
                 'tripolion', 'tryginon', 'trygon', 'typhonion', 'ulophonon', 'ulophyton', 'urion', 'xenon',
                 'xeromyron', 'xeron', 'xiphion', 'xyliglycon', 'xylion', 'xylon', 'xylophyton', 'zacon',
                 'zoophthalmon', 'zopyron', 'zopyrontion', 'zugon']


# Manually
n_exceptions += [
    "Tharan", "arcton", "Fison", # Fleuve
    "therapeuon"
]

n_exceptions = [tok.lower() for tok in n_exceptions]


normalize_space = re.compile(r"\s+")

# Dictionary of filenames -> Path
_xmls: Dict[str, str] = {
    op.basename(path): path
    for path in glob(XML_FILES, recursive=True)
}

has_word = re.compile(r".*\w+.*")


def get_text_object(ident: str) -> CapitainsCtsText:
    """ Given an identifier, gets a text from Capitains
    """
    filename = ident.split(":")[-1]+".xml"
    current_file = _xmls.get(filename)
    if current_file:
        return CapitainsCtsText(resource=parse(current_file))
    else:
        raise Exception("% not found".format(ident))


def minimal(text: str, annotations: List[Dict[str, str]]) -> Tuple[
                                                             int,
                                                             List[Dict[str, str]]]:
    """ Get the minimal amount of tokens and potentially cleans the order of the annotations"""
    print("Beginning", text)
    a_i = 0  # Annotation Index
    orig_text = text  # For debugging purposes
    before_current = ""
    # We make sure we have either text or annotations
    while a_i < len(annotations) and text:
        current = annotations[a_i]
        current_form = normalize_form(current["form"])
        next_form = "UNKNOWN"
        # If we have a next annotation, might be useful
        if a_i + 1 < len(annotations):
            next_form = annotations[a_i + 1]["form"]

        # Bug related ot PR #970 in CLTK
        if current_form.lower()+"n" in n_exceptions and next_form == "-ne":
            current_form = annotations[a_i]["form"] = current_form+"n"
            annotations = annotations[:a_i+1] + annotations[a_i+2:]  # Remove the -ne

        # To avoid unecessary step, we start the first index at the size of the original token
        index = len(current_form)
        if current["form"] == "-ne":
            index = 1

        text_length = len(text)

        found = False
        while index <= text_length:
            current_text = text[:index]
            # secum is tokenized as cum se by tokenizer...
            if current_text.endswith(next_form+"cum") and\
                    current_form == "cum":
                # We reorder annotations
                annotations = annotations[:a_i] + [annotations[a_i+1]] + [current] + annotations[a_i+2:]
                # We move one
                text = text[index:]
                before_current = orig_text[:len(before_current)+index]
                found = True
                a_i += 1  # We move one more because se is out
                break
            elif current_text.endswith(current_form):
                text = text[index:]
                before_current = orig_text[:len(before_current)+index]
                found = True
                break
            elif current["form"] == "-ne" and current_text.endswith("n") and not text[:index+1].endswith("ne"):
                text = text[index:]
                before_current = orig_text[:len(before_current)+index]
                found = True
                break

            index += 1

        if not found and has_word.match(text):
            print("Not found, stopping iterations")
            print("Treated before")
            tokenized = WordTokenizer("latin").tokenize(text)
            print("Tokenized", tokenized)
            #pprint(before_current)
            print("Index", index)
            print("Remaining text: ", text)
            print("Aligned toks: ", [tok["form"] for tok in annotations[:a_i]])
            print("Remaining toks: ", [tok["form"] for tok in annotations[a_i:]])
            print(annotations[:a_i])
            print("Help for test building")
            pprint([
                {"form": an["form"], "tag": str(i)}
                for i, an in enumerate(annotations[max(0, a_i-5):a_i+5])
            ])
            raise Exception

        if found:
            # If we still have annotation but the next token is longer than the remaining text
            #   WE STOP
            a_i += 1

            if a_i < len(annotations) and len(normalize_form(annotations[a_i]["form"])) > len(text):
                # Specific case of elision treated first here
                #   then in aligned
                striped = text.strip()
                if has_word.match(striped):  # Hyphenation were clean by transform
                    hyphenated = striped.split()[-1]  # Keep the end then remove the "-"
                    # If we the next form starts with the current text !
                    if next_form.startswith(hyphenated):
                        a_i += 1
                break
        else:
            break

    return a_i, annotations


def normalize_form(form: str) -> str:
    """ Removes additional characters from forms, namely "-" for enclitic"""
    if form.startswith("-"):
        return form[1:]
    return form


def get_match(pattern: str, string: str) -> Tuple[str, Optional[int], Optional[int]]:
    """ Find matches of pattern in a string, returns a boolean representing whether it was found
    as well as the start and end position eventually

    :param pattern: Form to find, potentially regexp formatted
    :param string: String in which to search
    :return: (Found or Not, Optional[Start position], Optional[End Position])
    """
    found = False
    s, e = None, None
    for match in re.finditer(pattern=pattern, string=string):
        if not found:
            s, e = match.start(), match.end()
            found = True
            break
    return found, s, e


def aligned(text: str, annotations: List[Dict[str, str]]) -> Tuple[
                                                             List[Union[str, Dict[str, str]]],
                                                             List[Dict[str, str]]
]:
    """ Aligns text with a list of annotations

    :param text: A string containing text tied to the annotation list
    :param annotations: List of annotation where we have at least a `form` key
    :return: List of [String, Dict] where strings are basically text between annotated form (mostly spaces)
        Returns a new version of annotations where we removed things that we found
    """
    start_text = ""+text  # Make a copy for debugging
    minimal_diff_nb_tokens, annotations = minimal(text, annotations)
    # If we are not emptying
    if minimal_diff_nb_tokens != len(annotations):
        tokens, annotations = annotations[:minimal_diff_nb_tokens], annotations[minimal_diff_nb_tokens:]
    else:
        tokens = annotations
        annotations = []

    alignement = []

    while text and tokens:

        pattern = normalize_form(tokens[0]["form"])
        # We search in the text the first token
        if tokens[0]["form"] == "-ne":
            pattern = r"ne|n"

        found, s, e = get_match(pattern, text)

        if not found:
            # We could have a damn hyphenation
            if has_word.match(text):
                # If we have an hyphenation, current form should hold something
                #   We start from the end !
                for word_length in reversed(range(len(pattern))):
                    found, s, e = get_match(pattern[:word_length], text)
                    if found:
                        # We need to store the end of the hyphenization in the annotations !
                        remains = pattern[e-s:]
                        tokens[0]["hyphen"] = "true"
                        annotations.insert(0, {"form": remains, "hyphen": "true"})
                        break
            if not found:
                print(pattern)
                print("Text [{}]".format(text))
                print(start_text)
                print("Tokens, ", " ".join([t["form"] for t in tokens]))
                print(tokens)
                raise Exception()

        # Otherwise, if the beginning of match is not 0, we have supplementary text
        if s != 0:
            alignement.append(text[:s])
        alignement.append(tokens.pop(0))
        text = text[e:]

    if tokens:
        print("Remaining tokens", tokens)
        print("Text", text)
        raise Exception("All tokens should be aligned !")

    if text:
        alignement.append(text)

    return alignement, annotations


def element_or_tail(str_or_dict: Union[str, Dict[str, str]]):
    """ Transforms an element as str or dict """
    if isinstance(str_or_dict, str):
        return str
    return Builder("token", str_or_dict["form"], **{key: val for key, val in str_or_dict.items() if key != "form"})


def run_tests():
    """ This is a suite of tests that checks I ain't breaking anything

    """
    # Dealing with Hyphenation
    hyphen = "plus pecudes rationis habent, quae numine motae"
    annotations = [{"form": "plus", "tag": "1"}, {"form": "pecudes", "tag": "2"}, {"form": "rationis", "tag": "3"},
                   {"form": "habent", "tag": "4"}, {"form": "quae", "tag": "5"}, {"form": "numine", "tag": "6"},
                   {"form": "motaenil", "tag": "7"}]

    assert aligned(hyphen, annotations) == ([{"form": "plus", "tag": "1"}, " ", {"form": "pecudes", "tag": "2"}, " ",
                                            {"form": "rationis", "tag": "3"}, " ", {"form": "habent", "tag": "4"}, ", ",
                                            {"form": "quae", "tag": "5"}, " ", {"form": "numine", "tag": "6"}, " ",
                                            {"form": "motaenil", "tag": "7", "hyphen": "true"}],
                                            [{"form": "nil", "hyphen": "true"}]), "Hyphen should be correctly treated"

    weird_issue = "enim utrumne ad praeclarum illut bonum facile perueniri putent"
    annotations = [{'form': 'parum', 'tag': '0'},
               {'form': 'o', 'tag': '1'},
               {'form': 'est', 'tag': '2'},
               {'form': 'ad', 'tag': '3'},
               {'form': 'bonum', 'tag': '4'},
               {'form': 'suscipiendum', 'tag': '5'},
               {'form': 'malum', 'tag': '6'},
               {'form': '-que', 'tag': '7'},
               {'form': 'fugiendum', 'tag': '8'},
               {'form': 'nisi', 'tag': '9'}]


if __name__ == "__main__":
    run_tests()
    texts = sorted(glob(op.join(PATH_TSV, "**", "*.tsv")) + glob(op.join(PATH_TSV, "**", ".tsv")), reverse=True)
    texts = [text for text in texts if "stoa0171" in text]
    for text in texts:

        with open(text) as tsv_io:
            tsv = []
            header = []
            for line_no, line in enumerate(tsv_io.readlines()):
                line = line.strip()
                if line:
                    if line_no == 0:
                        header = line.split("\t")
                    else:
                        tsv.append(dict(list(zip(header, line.split("\t")))))

        # We get identifiers connected to the item
        text_ident = op.split(op.dirname(text))[-1]
        passage_ident = op.basename(text).replace(".tsv", "")
        root = None
        depth = 0
        if passage_ident:
            root = passage_ident
            depth = passage_ident.count(".") + 1
        # We get the text medata
        print(text_ident)
        text_obj = get_text_object(text_ident)
        # Get the citation System
        citation = text_obj.citation
        # Set-up the current level citation
        current_level = citation[depth - 1]

        # Retrieve the same passage in XML
        root_passage: CapitainsCtsPassage = text_obj.getTextualNode(subreference=passage_ident)
        # Compute the maximum depth we have
        remaining_depth = len(current_level) - depth

        parent = Builder("root", text_id=text_ident, n=str(root_passage.reference))

        # Iterate over the passage
        for child in root_passage.getReffs(level=remaining_depth):
            print(text_ident, child)
            current = root_passage.getTextualNode(subreference=child)

            # Get plain text
            plain_text = normalize_space.sub(" ", transform(current.export(Mimetypes.PYTHON.ETREE))).strip()
            alignment, tsv = aligned(plain_text, annotations=tsv)

            print(ET.tostring(Builder("passage", n=str(child), *list(map(element_or_tail, alignment))), encoding=str,
                              pretty_print=True))
