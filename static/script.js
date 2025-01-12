document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mouseover', () => {
            button.style.backgroundColor = '#4364f7';
            button.style.transform = 'translateY(-5px)';
        });
        button.addEventListener('mouseout', () => {
            button.style.backgroundColor = '#0052d4';
            button.style.transform = 'translateY(0)';
        });
        button.addEventListener('mousedown', () => {
            button.style.backgroundColor = '#6fb1fc';
            button.style.transform = 'translateY(2px)';
        });
        button.addEventListener('mouseup', () => {
            button.style.backgroundColor = '#4364f7';
            button.style.transform = 'translateY(-5px)';
        });
    });
    document.addEventListener("DOMContentLoaded", function() {
        const back22 = document.querySelector('.back22');
        
        window.addEventListener('scroll', function() {
            const rect = back22.getBoundingClientRect();
            const inViewport = rect.top >= 0 && rect.bottom <= window.innerHeight;
        
            if (inViewport) {
            document.body.style.backgroundColor = "black";
            } else {
            document.body.style.backgroundColor = "white";
            }
        });
});
});

///////c CHATBOT
