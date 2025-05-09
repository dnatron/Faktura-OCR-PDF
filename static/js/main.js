/**
 * Hlavní JavaScript soubor pro aplikaci Faktura OCR PDF
 * Obsluhuje události HTMX, zpracování chyb a pomocné funkce pro formátování dat
 */

// Spuštění kódu po načtení stránky
document.addEventListener('DOMContentLoaded', function() {
    // Obsluha událostí HTMX
    
    // Událost před odesláním požadavku HTMX
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        // Globální zpracování před odesláním požadavku
        console.log('Požadavek začíná:', event.detail.requestConfig);
    });
    
    // Událost po dokončení požadavku HTMX
    document.body.addEventListener('htmx:afterRequest', function(event) {
        // Globální zpracování po dokončení požadavku
        console.log('Požadavek dokončen:', event.detail.xhr.status);
    });
    
    // Událost při chybě požadavku HTMX
    document.body.addEventListener('htmx:responseError', function(event) {
        // Výpis chyby do konzole
        console.error('Chyba požadavku:', event.detail.xhr.status, event.detail.xhr.responseText);
        
        // Zobrazení chybové zprávy uživateli
        const errorMessage = document.createElement('div'); // Vytvoření nového elementu
        errorMessage.className = 'error-message'; // Přiřazení třídy pro stylování
        errorMessage.innerHTML = `
            <div class="alert alert-error">
                <p><strong>Chyba:</strong> Nastala chyba při zpracování požadavku.</p>
                <p>Kód: ${event.detail.xhr.status}</p>
                <button class="close-btn">&times;</button>
            </div>
        `;
        
        // Přidání chybové zprávy do stránky
        document.body.appendChild(errorMessage);
        
        // Přidání obsluhy události pro tlačítko zavření
        errorMessage.querySelector('.close-btn').addEventListener('click', function() {
            errorMessage.remove(); // Odstranění chybové zprávy po kliknutí
        });
        
        // Automatické odstranění chybové zprávy po 5 sekundách
        setTimeout(() => {
            if (document.body.contains(errorMessage)) {
                errorMessage.remove();
            }
        }, 5000);
    });
    
    // Náhled nahraného souboru
    const fileInput = document.getElementById('file'); // Získání reference na input pro nahrávání souborů
    if (fileInput) {
        // Přidání obsluhy události při výběru souboru
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name; // Získání názvu vybraného souboru (pokud existuje)
            if (fileName) {
                // Zde by bylo možné přidat náhled souboru, pokud by bylo potřeba
                console.log('Vybrán soubor:', fileName);
            }
        });
    }
    
    // Automatické obnovení stavu zpracování
    const resultStatus = document.getElementById('result-status'); // Získání reference na element pro stav zpracování
    if (resultStatus) {
        // HTMX se stará o pravidelné dotazování na stav zpracování (polling)
        console.log('Sledování stavu zpracování...');
    }
});

/**
 * Pomocná funkce pro formátování měnových hodnot
 * @param {number} amount - Částka k formátování
 * @param {string} currency - Kód měny (výchozí je CZK)
 * @returns {string} Formátovaná částka s měnou
 */
function formatCurrency(amount, currency = 'CZK') {
    // Kontrola, zda je částka definována
    if (amount === null || amount === undefined) return 'N/A';
    
    // Formátování částky podle českých konvencí
    return new Intl.NumberFormat('cs-CZ', {
        style: 'currency',        // Formát měny
        currency: currency,       // Použitá měna
        minimumFractionDigits: 2  // Minimální počet desetinných míst
    }).format(amount);
}

/**
 * Pomocná funkce pro formátování data
 * @param {string} dateString - Datum ve formátu ISO string
 * @returns {string} Formátované datum podle českých konvencí
 */
function formatDate(dateString) {
    // Kontrola, zda je datum definováno
    if (!dateString) return 'N/A';
    
    // Převod na objekt Date a formátování podle českých konvencí
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('cs-CZ').format(date); // Formát: DD.MM.YYYY
}
