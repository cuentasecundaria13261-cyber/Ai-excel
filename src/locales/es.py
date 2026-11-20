"""Spanish text. The English sentence is the key; {placeholders} must match exactly."""

ES = {}

# ---- navigation, notices, AI access
ES.update({
    "Navigation": "Navegación",
    "Choose a dashboard": "Elige un panel",
    "Business Dashboard": "Panel de negocio",
    "Generic Dashboard": "Panel genérico",
    "Business (classic)": "Negocio (clásico)",
    "Free test version. Files are processed in memory and not saved by this app.":
        "Versión de prueba gratuita. Los archivos se procesan en memoria y esta app no los guarda.",
    "The original business dashboard (fixed column names)":
        "El panel de negocio original (nombres de columna fijos)",
    "Upload your sales file and get a plain-language summary, alerts and charts":
        "Sube tu archivo de ventas y obtén un resumen en lenguaje sencillo, alertas y gráficos",
    "Analyze any Excel or CSV dataset, whatever its columns are":
        "Analiza cualquier conjunto de datos de Excel o CSV, sin importar sus columnas",
    "**AI explanations run on your own computer**, so they are switched off on this website. "
    "Everything else on this page works without them: the summary, the alerts, the charts and the reports.":
        "**Las explicaciones con IA funcionan en tu propio computador**, por eso están desactivadas en este sitio web. "
        "Todo lo demás de esta página funciona sin ellas: el resumen, las alertas, los gráficos y los informes.",
    "**AI explanations on this website use a free online AI service (Groq).** "
    "If you continue, a summary is sent there: the totals, the names of groups such as products "
    "or regions, the alerts, and anything you type in the boxes above. "
    "Your file itself is not sent. Do not type personal data.":
        "**Las explicaciones con IA en este sitio usan un servicio de IA en línea gratuito (Groq).** "
        "Si continúas, se envía allí un resumen: los totales, los nombres de grupos como productos "
        "o regiones, las alertas y lo que escribas en los cuadros de arriba. "
        "Tu archivo en sí no se envía. No escribas datos personales.",
    "I understand, and I agree to send this summary to the online AI":
        "Entiendo y acepto enviar este resumen a la IA en línea",
    "AI requests left in this visit: {count}": "Solicitudes de IA que te quedan en esta visita: {count}",
    "The AI program (Ollama) is running on this computer, but the model **{model}** is not installed yet. "
    "Install it with this command, then reload the page:":
        "El programa de IA (Ollama) está funcionando en este computador, pero el modelo **{model}** aún no está instalado. "
        "Instálalo con este comando y luego recarga la página:",
    "How to turn on AI explanations (free)": "Cómo activar las explicaciones con IA (gratis)",
    "1. Install **Ollama** from ollama.com (free, runs on your computer).\n2. Download the model once:\n":
        "1. Instala **Ollama** desde ollama.com (gratis, funciona en tu computador).\n2. Descarga el modelo una sola vez:\n",
    "3. Download this project and start it on your computer:\n":
        "3. Descarga este proyecto e inícialo en tu computador:\n",
    "Your files then stay on your computer, and the AI button appears automatically.":
        "Así tus archivos se quedan en tu computador y el botón de IA aparece automáticamente.",
    "The free AI allowance for today has been used up. It starts again tomorrow.":
        "El cupo gratuito de IA de hoy se agotó. Vuelve a empezar mañana.",
    "The free AI allowance for today has been used up. It starts again tomorrow. Everything else on this page still works.":
        "El cupo gratuito de IA de hoy se agotó. Vuelve a empezar mañana. Todo lo demás de esta página sigue funcionando.",
    "You have used all the AI requests for this visit. Reload the page later to try again.":
        "Usaste todas las solicitudes de IA de esta visita. Recarga la página más tarde para intentarlo de nuevo.",
    "The AI is busy right now. Please try again in a minute.":
        "La IA está ocupada en este momento. Inténtalo de nuevo en un minuto.",
    "This dataset summary is too large for the free online AI. Try filtering the data first.":
        "El resumen de estos datos es demasiado grande para la IA gratuita en línea. Prueba primero a filtrar los datos.",
    "The online AI returned an error (HTTP {code}). Please try again.":
        "La IA en línea devolvió un error (HTTP {code}). Inténtalo de nuevo.",
    "Could not reach the online AI. Please try again in a moment.":
        "No se pudo conectar con la IA en línea. Inténtalo de nuevo en un momento.",
    "The online AI sent an answer the app could not read. Please try again.":
        "La IA en línea envió una respuesta que la app no pudo leer. Inténtalo de nuevo.",
    "The online AI rejected the app's key. The owner needs to check it.":
        "La IA en línea rechazó la clave de la app. El propietario debe revisarla.",
    "The free online AI is busy or its limit was reached. Please try again in a minute.":
        "La IA gratuita en línea está ocupada o se alcanzó su límite. Inténtalo de nuevo en un minuto.",
    "Free test version: your file is processed in memory during your visit and this app does not save it. "
    "Please do not upload personal data or files you are not allowed to share.":
        "Versión de prueba gratuita: tu archivo se procesa en memoria durante tu visita y esta app no lo guarda. "
        "Por favor, no subas datos personales ni archivos que no tengas permiso de compartir.",
    "Some columns look like personal data: {listing}. You do not need them for sales analysis, and keeping personal data out is safer.":
        "Algunas columnas parecen datos personales: {listing}. No las necesitas para analizar ventas y es más seguro no incluir datos personales.",
    "Remove these columns before analysis (recommended)": "Quitar estas columnas antes del análisis (recomendado)",
    "looks like an email address": "parece un correo electrónico",
    "looks like a phone number": "parece un número de teléfono",
    "looks like an address": "parece una dirección",
    "looks like an ID document": "parece un documento de identidad",
    "looks like a person's name": "parece el nombre de una persona",
})

# ---- upload and cleaning messages
ES.update({
    "This is a large file ({rows} rows). Everything still works, but it may take a few seconds to load and to react when you change something.":
        "Este es un archivo grande ({rows} filas). Todo sigue funcionando, pero puede tardar unos segundos en cargar y en reaccionar cuando cambies algo.",
    "This file is {size} MB. The free test version accepts files up to {limit} MB. Try a smaller export or fewer columns.":
        "Este archivo pesa {size} MB. La versión de prueba gratuita acepta archivos de hasta {limit} MB. Prueba con una exportación más pequeña o con menos columnas.",
    "This sheet has more than {limit} rows. The free test version handles up to {limit} rows. Filter the data or split it into smaller files.":
        "Esta hoja tiene más de {limit} filas. La versión de prueba gratuita admite hasta {limit} filas. Filtra los datos o divídelos en archivos más pequeños.",
    "This sheet has {count} columns. The free test version handles up to {limit} columns.":
        "Esta hoja tiene {count} columnas. La versión de prueba gratuita admite hasta {limit} columnas.",
    "This file has {count} rows. The free test version handles up to {limit} rows. Filter the data or split it into smaller files.":
        "Este archivo tiene {count} filas. La versión de prueba gratuita admite hasta {limit} filas. Filtra los datos o divídelos en archivos más pequeños.",
    "This file has {count} columns. The free test version handles up to {limit} columns.":
        "Este archivo tiene {count} columnas. La versión de prueba gratuita admite hasta {limit} columnas.",
    "This Excel file has an unusual structure and was not opened.":
        "Este archivo de Excel tiene una estructura inusual y no se abrió.",
    "This Excel file is far larger than it looks once opened, so it was not loaded. Try saving it again as a .csv.":
        "Este archivo de Excel es mucho más grande de lo que parece al abrirlo, por eso no se cargó. Prueba a guardarlo de nuevo como .csv.",
    "This does not look like a valid Excel (.xlsx) file. Open it in Excel and use Save As to create a new .xlsx or .csv.":
        "Esto no parece un archivo de Excel (.xlsx) válido. Ábrelo en Excel y usa Guardar como para crear un .xlsx o .csv nuevo.",
    "This does not look like a valid Excel (.xlsx) file.":
        "Esto no parece un archivo de Excel (.xlsx) válido.",
    "Unsupported file type. Use .csv, .xlsx or .xlsm.":
        "Tipo de archivo no admitido. Usa .csv, .xlsx o .xlsm.",
    "This Excel file is too large or unusual to open safely in the free test version. Try saving it again with fewer rows, or without images.":
        "Este archivo de Excel es demasiado grande o inusual para abrirlo de forma segura en la versión de prueba gratuita. Prueba a guardarlo de nuevo con menos filas o sin imágenes.",
    "This file has more than {limit} rows. The free test version handles up to {limit} rows. Please upload a smaller file, for example one period at a time.":
        "Este archivo tiene más de {limit} filas. La versión de prueba gratuita admite hasta {limit} filas. Sube un archivo más pequeño, por ejemplo un período a la vez.",
    "This file has more than {limit} columns. The free test version handles up to {limit} columns.":
        "Este archivo tiene más de {limit} columnas. La versión de prueba gratuita admite hasta {limit} columnas.",
    "Could not decode the CSV file: {error}": "No se pudo leer la codificación del archivo CSV: {error}",
    "Removed {count} completely empty column(s).": "Se quitaron {count} columna(s) completamente vacía(s).",
    "Removed {count} completely empty row(s).": "Se quitaron {count} fila(s) completamente vacía(s).",
    "Converted text to numbers in: {columns}.": "Se convirtió texto en números en: {columns}.",
    "Converted text to dates in: {columns}.": "Se convirtió texto en fechas en: {columns}.",
    "Dates in {columns} could be read as day/month or month/day; day/month was assumed. Change 'Order of day and month' above if that is wrong.":
        "Las fechas de {columns} se pueden leer como día/mes o mes/día; se asumió día/mes. Cambia «Orden de día y mes» arriba si no es correcto.",
    "Removed {count} duplicate row(s).": "Se quitaron {count} fila(s) duplicada(s).",
    "Dropped {count} row(s) that had missing values.": "Se eliminaron {count} fila(s) que tenían valores vacíos.",
    "Filled missing values (median for numbers, 'Unknown' for text; dates were left as they are).":
        "Se rellenaron los valores vacíos (mediana para números, 'Unknown' para texto; las fechas se dejaron como estaban).",
    "Kept {count} missing value(s) as they are.": "Se dejaron {count} valor(es) vacío(s) tal como están.",
    "No cleaning was needed.": "No hizo falta limpiar nada.",
    "Combined {files} files into one table of {rows} rows.": "Se combinaron {files} archivos en una sola tabla de {rows} filas.",
    "The files do not have exactly the same columns. Columns that are missing in a file are left empty.":
        "Los archivos no tienen exactamente las mismas columnas. Las columnas que faltan en un archivo se dejan vacías.",
    "{name}: used the first sheet ('{sheet}').": "{name}: se usó la primera hoja ('{sheet}').",
    "Removed columns that look like personal data: {columns}.": "Se quitaron columnas que parecen datos personales: {columns}.",
})

# ---- Business Dashboard screen
ES.update({
    "Upload your sales file. We tidy it, draw the charts and tell you what needs your attention - no Excel skills needed.":
        "Sube tu archivo de ventas. Nosotros lo ordenamos, dibujamos los gráficos y te decimos qué necesita tu atención. No hace falta saber Excel.",
    "Choose one or more Excel or CSV files": "Elige uno o más archivos de Excel o CSV",
    "Upload a file to get started. Any column names work - we match them for you.":
        "Sube un archivo para empezar. Sirven cualquier nombre de columna: nosotros los relacionamos por ti.",
    "Try it with sample data": "Probar con datos de ejemplo",
    "You are looking at made-up sample data. Upload your own file above to analyze it.":
        "Estás viendo datos de ejemplo inventados. Sube tu propio archivo arriba para analizarlo.",
    "Could not read the file: {error}": "No se pudo leer el archivo: {error}",
    "The file was read, but it has no data rows.": "Se leyó el archivo, pero no tiene filas de datos.",
    "No data is left after tidying the file.": "No quedan datos después de ordenar el archivo.",
    "No columns are left after removing personal data. Untick the box to keep them, or upload a different file.":
        "No quedan columnas después de quitar los datos personales. Desmarca la casilla para conservarlas o sube otro archivo.",
    "We matched your columns - check them": "Relacionamos tus columnas: revísalas",
    "Change a choice if we guessed wrong. Only the money column is really needed.":
        "Cambia una opción si nos equivocamos. Solo la columna de dinero es realmente necesaria.",
    "(none)": "(ninguna)",
    "Money earned (revenue / sales)": "Dinero ganado (ingresos / ventas)",
    "Date": "Fecha",
    "Product": "Producto",
    "Category": "Categoría",
    "Region / store / city": "Región / tienda / ciudad",
    "Order number": "Número de pedido",
    "Units sold (quantity)": "Unidades vendidas (cantidad)",
    "Price per unit": "Precio por unidad",
    "The same column is used for two different things. Check your choices.":
        "La misma columna se usa para dos cosas distintas. Revisa tus opciones.",
    "There is no data to analyze after matching the columns.": "No hay datos para analizar después de relacionar las columnas.",
    "What we tidied in your file": "Qué ordenamos en tu archivo",
    "{read} rows read, {used} rows used.": "{read} filas leídas, {used} filas usadas.",
    "Filter your data (optional)": "Filtra tus datos (opcional)",
    "Which sheet has your sales?": "¿Qué hoja tiene tus ventas?",
    "Dates": "Fechas",
    "Region": "Región",
    "Dates: {start} to {end}": "Fechas: {start} a {end}",
    "No rows match these filters. Clear a filter above.": "Ninguna fila cumple estos filtros. Quita un filtro de arriba.",
    "What happened": "Qué pasó",
    "Filtered: {filters}": "Filtrado: {filters}",
    "Things to look at": "Cosas para revisar",
    "Nothing unusual was detected.": "No se detectó nada inusual.",
    "Key numbers": "Números clave",
    "vs previous period": "vs. el período anterior",
    "Total {label}": "Total de {label}",
    "Orders": "Pedidos",
    "Records": "Registros",
    "Revenue": "Ingresos",
    "Average per order": "Promedio por pedido",
    "Units sold": "Unidades vendidas",
    "Changes compare the last {days} days ({current}) with the {days} days before ({previous}).":
        "Los cambios comparan los últimos {days} días ({current}) con los {days} días anteriores ({previous}).",
    "There is not enough dated data to compare periods.": "No hay suficientes datos con fecha para comparar períodos.",
    "Charts": "Gráficos",
    "Over time": "En el tiempo",
    "Products": "Productos",
    "Regions": "Regiones",
    "Categories": "Categorías",
    "Days of the week": "Días de la semana",
    "How much {label} you made, by {unit}": "Cuántos {label} tuviste, por {unit}",
    "Which products bring in the most {label}": "Qué productos aportan más {label}",
    "Which regions bring in the most {label}": "Qué regiones aportan más {label}",
    "Which categories bring in the most {label}": "Qué categorías aportan más {label}",
    "Which days of the week sell the most ({label})": "Qué días de la semana venden más ({label})",
    "Match a date, product or region column above to see charts.":
        "Relaciona una columna de fecha, producto o región arriba para ver gráficos.",
    "Explain it to me (AI)": "Explícamelo (IA)",
    "The AI reads the numbers above and explains them in plain words. It can make mistakes, so check anything important against the numbers.":
        "La IA lee los números de arriba y los explica con palabras sencillas. Puede equivocarse, así que compara lo importante con los números.",
    "Is there something you want to know? (optional)": "¿Hay algo que quieras saber? (opcional)",
    "For example: why are sales going down?": "Por ejemplo: ¿por qué están bajando las ventas?",
    "Explain with AI": "Explicar con IA",
    "The AI is reading your numbers...": "La IA está leyendo tus números...",
    "Error generating AI insights: {error}": "Error al generar las explicaciones de IA: {error}",
    "This explanation was made for a different file, columns or filters than the ones selected now.":
        "Esta explicación se hizo para otro archivo, otras columnas u otros filtros distintos a los seleccionados ahora.",
    "Take it with you": "Llévatelo contigo",
    "Best products": "Mejores productos",
    "Business report": "Informe de negocio",
    "Download report (web page)": "Descargar informe (página web)",
    "Download report (PDF)": "Descargar informe (PDF)",
    "The PDF could not be created: {error}": "No se pudo crear el PDF: {error}",
    "For a PDF file: open the web page report and choose Print, then Save as PDF. Or install the optional package with: pip install reportlab":
        "Para un archivo PDF: abre el informe en página web, elige Imprimir y luego Guardar como PDF. O instala el paquete opcional con: pip install reportlab",
    "Download the tidied data (CSV)": "Descargar los datos ordenados (CSV)",
    "day": "día",
    "week": "semana",
    "month": "mes",
})

# ---- alerts and summary (written by Python so they are always exact)
ES.update({
    "n/a": "n/d",
    "Mon": "Lun", "Tue": "Mar", "Wed": "Mié", "Thu": "Jue", "Fri": "Vie", "Sat": "Sáb", "Sun": "Dom",
    "{start} to {end}": "{start} a {end}",
    "There is no revenue column, so revenue = units sold x price per unit.":
        "No hay columna de ingresos, así que ingresos = unidades vendidas x precio por unidad.",
    "No money column was found, so each row counts as one record. Pick a revenue column above for money totals.":
        "No se encontró una columna de dinero, así que cada fila cuenta como un registro. Elige arriba una columna de ingresos para ver totales de dinero.",
    "{bad} row(s) have no usable date and are left out of trends.":
        "{bad} fila(s) no tienen una fecha utilizable y quedan fuera de las tendencias.",
    "Removed {count} exact duplicate row(s) (same order number and values).":
        "Se quitaron {count} fila(s) duplicada(s) exactas (mismo número de pedido y mismos valores).",
    "{copies} row(s) are identical to another row. They were kept because there is no order number to prove they are duplicates.":
        "{copies} fila(s) son idénticas a otra fila. Se conservaron porque no hay número de pedido que demuestre que son duplicadas.",
    "{metric_label} fell sharply": "Los {label} cayeron con fuerza",
    "{metric_label} is going down": "Los {label} están bajando",
    "{metric_label} is growing strongly": "Los {label} están creciendo con fuerza",
    "In the last {days} days, {label} was {current}, {pct} lower than the {days} days before ({previous}).":
        "En los últimos {days} días, los {label} fueron {current}, un {pct} menos que en los {days} días anteriores ({previous}).",
    "In the last {days} days, {label} was {current}, {pct} higher than the {days} days before ({previous}).":
        "En los últimos {days} días, los {label} fueron {current}, un {pct} más que en los {days} días anteriores ({previous}).",
    " and {more} more": " y {more} más",
    "No sales at all for: {names}{extra}": "Sin ninguna venta: {names}{extra}",
    "This product sold before but had no sales in the last {days} days.":
        "Este producto se vendía antes, pero no tuvo ventas en los últimos {days} días.",
    "These products sold before but had no sales in the last {days} days.":
        "Estos productos se vendían antes, pero no tuvieron ventas en los últimos {days} días.",
    "This region sold before but had no sales in the last {days} days.":
        "Esta región vendía antes, pero no tuvo ventas en los últimos {days} días.",
    "These regions sold before but had no sales in the last {days} days.":
        "Estas regiones vendían antes, pero no tuvieron ventas en los últimos {days} días.",
    "This category sold before but had no sales in the last {days} days.":
        "Esta categoría vendía antes, pero no tuvo ventas en los últimos {days} días.",
    "These categories sold before but had no sales in the last {days} days.":
        "Estas categorías vendían antes, pero no tuvieron ventas en los últimos {days} días.",
    "Product '{name}' dropped a lot": "El producto '{name}' cayó mucho",
    "Region '{name}' dropped a lot": "La región '{name}' cayó mucho",
    "Category '{name}' dropped a lot": "La categoría '{name}' cayó mucho",
    "{metric_label} went from {previous} to {current} ({pct}) compared with the previous {days} days.":
        "Los {label} pasaron de {previous} a {current} ({pct}) frente a los {days} días anteriores.",
    "Unusual day: {date}": "Día inusual: {date}",
    "{metric_label} that day was {value}, much higher than a typical day with sales (about {typical}).":
        "Ese día los {label} fueron {value}, mucho más altos que un día típico con ventas (alrededor de {typical}).",
    "{metric_label} that day was {value}, much lower than a typical day with sales (about {typical}).":
        "Ese día los {label} fueron {value}, mucho más bajos que un día típico con ventas (alrededor de {typical}).",
    "Most {label} depends on one product": "La mayor parte de los {label} depende de un solo producto",
    "Most {label} depends on one region": "La mayor parte de los {label} depende de una sola región",
    "'{name}' brings {pct} of all {label}.": "'{name}' aporta el {pct} de todos los {label}.",
    "Some sales are negative": "Algunas ventas son negativas",
    "{count} row(s) have negative {label} (returns, refunds or typing mistakes).":
        "{count} fila(s) tienen {label} negativos (devoluciones, reembolsos o errores de digitación).",
    "Some rows have no date": "Algunas filas no tienen fecha",
    "{count} row(s) were left out of the time charts and comparisons.":
        "{count} fila(s) quedaron fuera de los gráficos en el tiempo y de las comparaciones.",
    "From {start} to {end} there are {count} records.": "Del {start} al {end} hay {count} registros.",
    "From {start} to {end} there were {count} orders and {money} in {label}.":
        "Del {start} al {end} hubo {count} pedidos y {money} en {label}.",
    "From {start} to {end} there were {count} records and {money} in {label}.":
        "Del {start} al {end} hubo {count} registros y {money} en {label}.",
    "There are {count} records.": "Hay {count} registros.",
    "There are {count} orders with {money} in {label}.": "Hay {count} pedidos con {money} en {label}.",
    "There are {count} records with {money} in {label}.": "Hay {count} registros con {money} en {label}.",
    "In the last {n} days {label} was {current}; there is nothing in the {n} days before to compare with.":
        "En los últimos {n} días los {label} fueron {current}; no hay nada en los {n} días anteriores con qué comparar.",
    "In the last {n} days {label} was {current}, up {pct} compared with the {n} days before ({previous}).":
        "En los últimos {n} días los {label} fueron {current}, un {pct} más que en los {n} días anteriores ({previous}).",
    "In the last {n} days {label} was {current}, down {pct} compared with the {n} days before ({previous}).":
        "En los últimos {n} días los {label} fueron {current}, un {pct} menos que en los {n} días anteriores ({previous}).",
    "Best product: {name} ({pct} of {label}).": "Mejor producto: {name} ({pct} de los {label}).",
    "Best region: {name} ({pct} of {label}).": "Mejor región: {name} ({pct} de los {label}).",
    "{count} thing(s) need your attention - see the alerts below.":
        "{count} cosa(s) necesitan tu atención: mira las alertas de abajo.",
})

# ---- report
ES.update({
    "Created {when}": "Creado el {when}",
    "Urgent": "Urgente",
    "Look at this": "Revisa esto",
    "Good to know": "Bueno saber",
    "Value": "Valor",
    "Change vs previous period": "Cambio frente al período anterior",
    "Latest period: {current}. Previous period: {previous}.": "Último período: {current}. Período anterior: {previous}.",
    "Name": "Nombre",
    "{metric} over time (by {unit})": "{metric} en el tiempo (por {unit})",
    "Explained in plain words (AI)": "Explicado con palabras sencillas (IA)",
    "What you could do": "Qué podrías hacer",
    "Why:": "Por qué:",
    "why:": "por qué:",
    "Keep in mind:": "Ten en cuenta:",
    "AI-written text can contain mistakes. Check important numbers against the tables above.":
        "El texto escrito por la IA puede tener errores. Compara los números importantes con las tablas de arriba.",
    "AI-written text can contain mistakes. Check important numbers against the tables.":
        "El texto escrito por la IA puede tener errores. Compara los números importantes con las tablas.",
})

# ---- feedback box
ES.update({
    "Send feedback": "Enviar comentarios",
    "Tell us what worked and what did not. Please do not write personal data or paste your file's contents here.":
        "Cuéntanos qué funcionó y qué no. Por favor, no escribas datos personales ni pegues el contenido de tu archivo aquí.",
    "How useful was it?": "¿Qué tan útil fue?",
    "Very useful": "Muy útil",
    "Useful": "Útil",
    "So-so": "Regular",
    "Not useful": "No fue útil",
    "About": "Sobre",
    "General": "General",
    "Something is broken": "Algo no funciona",
    "An idea": "Una idea",
    "Confusing": "Confuso",
    "Your feedback": "Tus comentarios",
    "What did you try? What would make it better?": "¿Qué probaste? ¿Qué lo mejoraría?",
    "Email, only if you want a reply (optional)": "Correo, solo si quieres una respuesta (opcional)",
    "Send": "Enviar",
    "Thanks! Please wait a few seconds before sending another one.":
        "¡Gracias! Espera unos segundos antes de enviar otro.",
    "Please write a message first.": "Por favor, escribe primero un mensaje.",
    "Thank you! Your feedback was sent.": "¡Gracias! Tus comentarios fueron enviados.",
    "Sorry, your feedback could not be sent. Please try again later.":
        "Lo sentimos, no se pudieron enviar tus comentarios. Inténtalo de nuevo más tarde.",
    "Or report it on GitHub": "O repórtalo en GitHub",
    "You can also write to us: {email}": "También puedes escribirnos: {email}",
})

# ---- Generic Dashboard screen
ES.update({
    "Upload any Excel or CSV file. The app detects what each column is, cleans the data and explains it with AI, whatever the columns are.":
        "Sube cualquier archivo de Excel o CSV. La app detecta qué es cada columna, limpia los datos y los explica con IA, sin importar cuáles sean las columnas.",
    "Choose an Excel or CSV file": "Elige un archivo de Excel o CSV",
    "Upload a file to get started.": "Sube un archivo para empezar.",
    "Sheet to analyze": "Hoja para analizar",
    "Reading options": "Opciones de lectura",
    "Header row (1 = first row of the sheet)": "Fila de encabezados (1 = primera fila de la hoja)",
    "Could not open the Excel file: {error}": "No se pudo abrir el archivo de Excel: {error}",
    "File uploaded and read successfully!": "¡Archivo subido y leído correctamente!",
    "Data cleaning": "Limpieza de datos",
    "Remove duplicate rows": "Quitar filas duplicadas",
    "Convert numbers stored as text (for example $1,200)": "Convertir números guardados como texto (por ejemplo $1,200)",
    "Detect and convert date columns": "Detectar y convertir columnas de fechas",
    "How should missing values be handled?": "¿Cómo se deben tratar los valores vacíos?",
    "Keep missing values": "Conservar los valores vacíos",
    "Drop rows with missing values": "Eliminar las filas con valores vacíos",
    "Fill (median for numbers, 'Unknown' for text)": "Rellenar (mediana para números, 'Unknown' para texto)",
    "Order of day and month in text dates": "Orden de día y mes en las fechas de texto",
    "Detect automatically": "Detectar automáticamente",
    "Day first (31/12/2024)": "Día primero (31/12/2024)",
    "Month first (12/31/2024)": "Mes primero (12/31/2024)",
    "No rows are left after cleaning. Try keeping the missing values.":
        "No quedan filas después de limpiar. Prueba a conservar los valores vacíos.",
    "What the cleaning did": "Qué hizo la limpieza",
    "Original rows": "Filas originales",
    "Cleaned rows": "Filas limpias",
    "Columns": "Columnas",
    "Cleaned dataset preview": "Vista previa de los datos limpios",
    "Download Cleaned CSV": "Descargar CSV limpio",
    "Column roles": "Roles de las columnas",
    "The app guessed what each column is. Change any that look wrong: measure = a number to analyze, dimension = a category to group by, date = a time column, id / text / ignore = not used for comparisons.":
        "La app adivinó qué es cada columna. Cambia las que veas mal: measure = un número para analizar, dimension = una categoría para agrupar, date = una columna de tiempo, id / text / ignore = no se usan para comparar.",
    "Analysis settings": "Ajustes del análisis",
    "Main metric": "Métrica principal",
    "No numeric column found, so only record counts will be analyzed.":
        "No se encontró ninguna columna numérica, así que solo se analizará el conteo de registros.",
    "Date column": "Columna de fecha",
    "No date column found, so time trends will be skipped.":
        "No se encontró ninguna columna de fecha, así que se omitirán las tendencias en el tiempo.",
    "How to combine values in a group": "Cómo combinar los valores de un grupo",
    "Total (sum)": "Total (suma)",
    "Average (mean)": "Promedio (media)",
    "Columns to compare (groups)": "Columnas para comparar (grupos)",
    "Could not calculate the analytics: {error}": "No se pudo calcular el análisis: {error}",
    "Overview": "Resumen general",
    "Rows": "Filas",
    "Total {name}": "Total de {name}",
    "{name}: average {average}, median {median}, minimum {minimum}, maximum {maximum}.":
        "{name}: promedio {average}, mediana {median}, mínimo {minimum}, máximo {maximum}.",
    "{name} by {group}": "{name} por {group}",
    "{name} by month": "{name} por mes",
    "Calculated facts (what the AI receives)": "Datos calculados (lo que recibe la IA)",
    "AI Insights": "Explicaciones de IA",
    "What do you want to learn? (optional)": "¿Qué quieres saber? (opcional)",
    "For example: which groups should we focus on?": "Por ejemplo: ¿en qué grupos deberíamos concentrarnos?",
    "Short description of this dataset (optional)": "Descripción corta de estos datos (opcional)",
    "For example: monthly support tickets of a software company":
        "Por ejemplo: tickets de soporte mensuales de una empresa de software",
    "Generate AI Insights": "Generar explicaciones con IA",
    "Generating AI insights...": "Generando explicaciones con IA...",
    "Generated from the settings you had when you clicked the button.":
        "Generado con los ajustes que tenías cuando hiciste clic en el botón.",
})

# ---- AI report display
ES.update({
    "Evidence: {line}": "Evidencia: {line}",
    "The AI response had some issues, but it is shown below.": "La respuesta de la IA tuvo algunos problemas, pero se muestra abajo.",
    "Validation issues": "Problemas de validación",
    "The AI did not return a usable report. Please try again.": "La IA no devolvió un informe utilizable. Inténtalo de nuevo.",
    "Executive summary": "Resumen ejecutivo",
    "No summary generated.": "No se generó ningún resumen.",
    "Key observations": "Observaciones clave",
    "No significant observations identified.": "No se identificaron observaciones importantes.",
    "Recommendations": "Recomendaciones",
    "Action": "Acción",
    "Reason:": "Motivo:",
    "Caveat:": "Salvedad:",
    "No recommendations at this time.": "Por ahora no hay recomendaciones.",
    "Data quality": "Calidad de los datos",
    "No data quality issues identified.": "No se identificaron problemas de calidad de los datos.",
    "Further analysis opportunities": "Otros análisis posibles",
    "needs:": "necesita:",
    "No further analysis suggestions.": "No hay más sugerencias de análisis.",
    "Analysis limitations": "Límites del análisis",
    "AI-generated from the calculated facts. Check important numbers against the tables and charts above.":
        "Generado por IA a partir de los datos calculados. Compara los números importantes con las tablas y gráficos de arriba.",
})
