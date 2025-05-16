// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Animation pour les messages flash
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(message);
            bsAlert.close();
        }, 5000);
    });
    
    // Confirmation de suppression
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.')) {
                e.preventDefault();
            }
        });
    });
    
    // Date picker en français
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.setAttribute('data-placeholder', this.placeholder);
            this.placeholder = 'JJ/MM/AAAA';
        });
        
        input.addEventListener('blur', function() {
            this.placeholder = this.getAttribute('data-placeholder') || '';
        });
    });
});