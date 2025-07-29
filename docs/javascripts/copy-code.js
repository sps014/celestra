// Copy code functionality for MkDocs documentation
document.addEventListener('DOMContentLoaded', function() {
    // Add copy buttons to all code blocks
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(function(codeBlock) {
        const pre = codeBlock.parentElement;
        
        // Skip if already has copy button
        if (pre.querySelector('.copy-button')) {
            return;
        }
        
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.textContent = 'Copy';
        copyButton.setAttribute('aria-label', 'Copy code to clipboard');
        
        // Add button to pre element
        pre.appendChild(copyButton);
        
        // Add click event
        copyButton.addEventListener('click', function() {
            const code = codeBlock.textContent;
            
            // Copy to clipboard
            navigator.clipboard.writeText(code).then(function() {
                // Show success state
                copyButton.textContent = 'Copied!';
                copyButton.classList.add('copied');
                
                // Reset after 2 seconds
                setTimeout(function() {
                    copyButton.textContent = 'Copy';
                    copyButton.classList.remove('copied');
                }, 2000);
            }).catch(function(err) {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = code;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                // Show success state
                copyButton.textContent = 'Copied!';
                copyButton.classList.add('copied');
                
                // Reset after 2 seconds
                setTimeout(function() {
                    copyButton.textContent = 'Copy';
                    copyButton.classList.remove('copied');
                }, 2000);
            });
        });
    });
    
    // Add copy buttons to inline code blocks (for syntax highlighting)
    const highlightedCodeBlocks = document.querySelectorAll('pre');
    
    highlightedCodeBlocks.forEach(function(pre) {
        // Skip if already has copy button
        if (pre.querySelector('.copy-button')) {
            return;
        }
        
        // Find the code content
        let codeContent = '';
        const codeElement = pre.querySelector('code');
        if (codeElement) {
            codeContent = codeElement.textContent;
        } else {
            codeContent = pre.textContent;
        }
        
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.textContent = 'Copy';
        copyButton.setAttribute('aria-label', 'Copy code to clipboard');
        
        // Add button to pre element
        pre.appendChild(copyButton);
        
        // Add click event
        copyButton.addEventListener('click', function() {
            // Copy to clipboard
            navigator.clipboard.writeText(codeContent).then(function() {
                // Show success state
                copyButton.textContent = 'Copied!';
                copyButton.classList.add('copied');
                
                // Reset after 2 seconds
                setTimeout(function() {
                    copyButton.textContent = 'Copy';
                    copyButton.classList.remove('copied');
                }, 2000);
            }).catch(function(err) {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = codeContent;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                // Show success state
                copyButton.textContent = 'Copied!';
                copyButton.classList.add('copied');
                
                // Reset after 2 seconds
                setTimeout(function() {
                    copyButton.textContent = 'Copy';
                    copyButton.classList.remove('copied');
                }, 2000);
            });
        });
    });
    
    // Handle dynamic content (for single-page apps)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const newCodeBlocks = node.querySelectorAll ? node.querySelectorAll('pre code') : [];
                        const newPreBlocks = node.querySelectorAll ? node.querySelectorAll('pre') : [];
                        
                        // Add copy buttons to new code blocks
                        newCodeBlocks.forEach(function(codeBlock) {
                            const pre = codeBlock.parentElement;
                            if (pre && !pre.querySelector('.copy-button')) {
                                const copyButton = document.createElement('button');
                                copyButton.className = 'copy-button';
                                copyButton.textContent = 'Copy';
                                copyButton.setAttribute('aria-label', 'Copy code to clipboard');
                                
                                pre.appendChild(copyButton);
                                
                                copyButton.addEventListener('click', function() {
                                    const code = codeBlock.textContent;
                                    navigator.clipboard.writeText(code).then(function() {
                                        copyButton.textContent = 'Copied!';
                                        copyButton.classList.add('copied');
                                        setTimeout(function() {
                                            copyButton.textContent = 'Copy';
                                            copyButton.classList.remove('copied');
                                        }, 2000);
                                    });
                                });
                            }
                        });
                        
                        // Add copy buttons to new pre blocks
                        newPreBlocks.forEach(function(pre) {
                            if (!pre.querySelector('.copy-button')) {
                                const codeElement = pre.querySelector('code');
                                const codeContent = codeElement ? codeElement.textContent : pre.textContent;
                                
                                const copyButton = document.createElement('button');
                                copyButton.className = 'copy-button';
                                copyButton.textContent = 'Copy';
                                copyButton.setAttribute('aria-label', 'Copy code to clipboard');
                                
                                pre.appendChild(copyButton);
                                
                                copyButton.addEventListener('click', function() {
                                    navigator.clipboard.writeText(codeContent).then(function() {
                                        copyButton.textContent = 'Copied!';
                                        copyButton.classList.add('copied');
                                        setTimeout(function() {
                                            copyButton.textContent = 'Copy';
                                            copyButton.classList.remove('copied');
                                        }, 2000);
                                    });
                                });
                            }
                        });
                    }
                });
            }
        });
    });
    
    // Start observing
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}); 