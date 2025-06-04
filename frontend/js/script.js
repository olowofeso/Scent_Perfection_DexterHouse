document.addEventListener('DOMContentLoaded', () => {
    const signInToggle = document.getElementById('signInToggle');
    const signUpToggle = document.getElementById('signUpToggle');
    const signInForm = document.getElementById('signInForm');
    const signUpForm = document.getElementById('signUpForm');

    // Input fields for validation
    const signInEmail = document.getElementById('signInEmail');
    const signInPassword = document.getElementById('signInPassword');
    const signUpEmail = document.getElementById('signUpEmail');
    const signUpPassword = document.getElementById('signUpPassword');
    const confirmPassword = document.getElementById('confirmPassword');

    // Error message elements
    const signInEmailError = document.getElementById('signInEmailError');
    const signInPasswordError = document.getElementById('signInPasswordError');
    const signUpEmailError = document.getElementById('signUpEmailError');
    const signUpPasswordError = document.getElementById('signUpPasswordError');
    const confirmPasswordError = document.getElementById('confirmPasswordError');

    // Function to show a form
    function showForm(formToShow, formToHide) {
        formToHide.classList.remove('active');
        formToHide.style.transform = 'translateX(-100%)'; // Slide out left
        formToHide.style.opacity = '0';

        // Give a slight delay before sliding in the new form for a smoother transition
        setTimeout(() => {
            formToHide.style.display = 'none'; // Hide completely after animation
            formToShow.style.display = 'block'; // Make visible to start animation
            formToShow.style.transform = 'translateX(0)'; // Slide in
            formToShow.style.opacity = '1';
        }, 500); // This duration should match your CSS transition duration
    }

    signInToggle.addEventListener('click', () => {
        signInToggle.classList.add('active');
        signUpToggle.classList.remove('active');
        showForm(signInForm, signUpForm);
    });

    signUpToggle.addEventListener('click', () => {
        signUpToggle.classList.add('active');
        signInToggle.classList.remove('active');
        showForm(signUpForm, signInForm);
    });

    // --- Client-side Validation Functions ---

    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    function validatePassword(password) {
        // At least 8 characters, one uppercase, one lowercase, one number, one special character
        const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$/;
        return re.test(password);
    }

    function displayError(element, message) {
        element.textContent = message;
    }

    function clearError(element) {
        element.textContent = '';
    }

    // Sign In Form Validation
    signInForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent default form submission

        let isValid = true;

        // Email/Username validation (basic check for non-empty)
        if (signInEmail.value.trim() === '') {
            displayError(signInEmailError, 'Email or username is required.');
            isValid = false;
        } else {
            clearError(signInEmailError);
        }

        // Password validation (basic check for non-empty)
        if (signInPassword.value.trim() === '') {
            displayError(signInPasswordError, 'Password is required.');
            isValid = false;
        } else {
            clearError(signInPasswordError);
        }

        if (isValid) {
            // Here you would send data to your backend
            console.log('Sign In form submitted:', {
                email: signInEmail.value,
                password: signInPassword.value
            });
            alert('Sign In Successful (simulated)!'); // Replace with actual success handling
            // window.location.href = 'first-time-login.html'; // Redirect on success
        }
    });

    // Sign Up Form Validation
    signUpForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent default form submission

        let isValid = true;

        if (!isValidEmail(signUpEmail.value.trim())) {
            displayError(signUpEmailError, 'Please enter a valid email address.');
            isValid = false;
        } else {
            clearError(signUpEmailError);
        }

        if (!validatePassword(signUpPassword.value)) {
            displayError(signUpPasswordError, 'Password must be at least 8 characters, with uppercase, lowercase, number, and special character.');
            isValid = false;
        } else {
            clearError(signUpPasswordError);
        }

        if (signUpPassword.value !== confirmPassword.value) {
            displayError(confirmPasswordError, 'Passwords do not match.');
            isValid = false;
        } else {
            clearError(confirmPasswordError);
        }

        if (isValid) {
            // Here you would send data to your backend
            console.log('Sign Up form submitted:', {
                email: signUpEmail.value,
                password: signUpPassword.value
            });
            alert('Account Creation Successful (simulated)!'); // Replace with actual success handling
            // window.location.href = 'first-time-login.html'; // Redirect on success
        }
    });

    // Add real-time validation on input blur (when user clicks out of field)
    signInEmail.addEventListener('blur', () => {
        if (signInEmail.value.trim() === '') {
            displayError(signInEmailError, 'Email or username is required.');
        } else {
            clearError(signInEmailError);
        }
    });

    signInPassword.addEventListener('blur', () => {
        if (signInPassword.value.trim() === '') {
            displayError(signInPasswordError, 'Password is required.');
        } else {
            clearError(signInPasswordError);
        }
    });

    signUpEmail.addEventListener('blur', () => {
        if (!isValidEmail(signUpEmail.value.trim())) {
            displayError(signUpEmailError, 'Please enter a valid email address.');
        } else {
            clearError(signUpEmailError);
        }
    });

    signUpPassword.addEventListener('blur', () => {
        if (!validatePassword(signUpPassword.value)) {
            displayError(signUpPasswordError, 'Password must be at least 8 characters, with uppercase, lowercase, number, and special character.');
        } else {
            clearError(signUpPasswordError);
        }
    });

    confirmPassword.addEventListener('blur', () => {
        if (signUpPassword.value !== confirmPassword.value) {
            displayError(confirmPasswordError, 'Passwords do not match.');
        } else {
            clearError(confirmPasswordError);
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const profileQuestionsForm = document.getElementById('profileQuestionsForm');

    if (profileQuestionsForm) { // Ensure this script only runs on the correct page
        const ageInput = document.getElementById('age');
        const weightInput = document.getElementById('weight');
        const heightInput = document.getElementById('height');
        const sexInput = document.getElementById('sex');
        const styleInput = document.getElementById('style');
        const raceInput = document.getElementById('race');

        const ageError = document.getElementById('ageError');
        const weightError = document.getElementById('weightError');
        const heightError = document.getElementById('heightError');
        const sexError = document.getElementById('sexError');
        const styleError = document.getElementById('styleError');
        const raceError = document.getElementById('raceError');

        function displayError(element, message) {
            element.textContent = message;
        }

        function clearError(element) {
            element.textContent = '';
        }

        profileQuestionsForm.addEventListener('submit', (event) => {
            event.preventDefault();
            let isValid = true;

            // Basic validation for all fields
            if (ageInput.value === '' || ageInput.value < 13 || ageInput.value > 120) {
                displayError(ageError, 'Please enter a valid age (13-120).');
                isValid = false;
            } else {
                clearError(ageError);
            }

            if (weightInput.value === '' || weightInput.value < 20) {
                displayError(weightError, 'Please enter a valid weight (min 20kg).');
                isValid = false;
            } else {
                clearError(weightError);
            }

            if (heightInput.value === '' || heightInput.value < 50) {
                displayError(heightError, 'Please enter a valid height (min 50cm).');
                isValid = false;
            } else {
                clearError(heightError);
            }

            if (sexInput.value === '') {
                displayError(sexError, 'Please select your biological sex.');
                isValid = false;
            } else {
                clearError(sexError);
            }

            if (styleInput.value === '') {
                displayError(styleError, 'Please select your personal style.');
                isValid = false;
            } else {
                clearError(styleError);
            }

            if (raceInput.value === '') {
                displayError(raceError, 'Please select your racial group.');
                isValid = false;
            } else {
                clearError(raceError);
            }

            if (isValid) {
                // Collect data
                const userData = {
                    age: ageInput.value,
                    weight: weightInput.value,
                    height: heightInput.value,
                    sex: sexInput.value,
                    style: styleInput.value,
                    race: raceInput.value
                };
                console.log('User data collected:', userData);

                // Send data to backend (using Fetch API)
                // Replace with your actual API endpoint
                /*
                fetch('/api/user/profile', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer YOUR_AUTH_TOKEN' // If authenticated
                    },
                    body: JSON.stringify(userData)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Profile updated successfully:', data);
                    alert('Profile updated successfully! Redirecting to perfume entry.');
                    window.location.href = 'perfume-entry.html'; // Redirect to next page
                })
                .catch(error => {
                    console.error('Error submitting profile data:', error);
                    alert('There was an error updating your profile. Please try again.');
                });
                */
                alert('Profile data submitted (simulated)! Redirecting to perfume entry.');
                window.location.href = 'perfume-entry.html'; // Simulate redirect
            }
        });

        // Add blur listeners for real-time validation feedback
        ageInput.addEventListener('blur', () => {
            if (ageInput.value === '' || ageInput.value < 13 || ageInput.value > 120) {
                displayError(ageError, 'Please enter a valid age (13-120).');
            } else {
                clearError(ageError);
            }
        });
        weightInput.addEventListener('blur', () => {
            if (weightInput.value === '' || weightInput.value < 20) {
                displayError(weightError, 'Please enter a valid weight (min 20kg).');
            } else {
                clearError(weightError);
            }
        });
        heightInput.addEventListener('blur', () => {
            if (heightInput.value === '' || heightInput.value < 50) {
                displayError(heightError, 'Please enter a valid height (min 50cm).');
            } else {
                clearError(heightError);
            }
        });
        sexInput.addEventListener('change', () => { // Use 'change' for select elements
            if (sexInput.value === '') {
                displayError(sexError, 'Please select your biological sex.');
            } else {
                clearError(sexError);
            }
        });
        styleInput.addEventListener('change', () => {
            if (styleInput.value === '') {
                displayError(styleError, 'Please select your personal style.');
            } else {
                clearError(styleError);
            }
        });
        raceInput.addEventListener('change', () => {
            if (raceInput.value === '') {
                displayError(raceError, 'Please select your racial group.');
            } else {
                clearError(raceError);
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('actualLoginForm');
    if (loginForm) { // Check if this is the login page
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            if (!email || !password) {
                alert('Please enter both email and password.');
                return;
            }

            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email, password: password }),
            })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(({ status, body }) => {
                if (status === 200) {
                    if (body.redirect_url) {
                        window.location.href = body.redirect_url;
                    } else {
                        alert(body.message || 'Login successful! Redirecting...');
                        // Fallback redirect if needed, though backend should always provide it
                        window.location.href = '/chatbot.html';
                    }
                } else {
                    alert('Login failed: ' + (body.message || 'Invalid email or password.'));
                }
            })
            .catch(error => {
                console.error('Login error:', error);
                alert('An error occurred during login. Please try again.');
            });
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const perfumeNameInput = document.getElementById('perfumeNameInput');
    const addPerfumeBtn = document.getElementById('addPerfumeBtn');
    const perfumeList = document.getElementById('perfumeList');
    const goToChatbotBtn = document.getElementById('goToChatbotBtn');

    // Simulate owned perfumes (in a real app, this would come from the backend)
    let ownedPerfumes = []; // Start with an empty array or load from storage

    function renderPerfumeList() {
        perfumeList.innerHTML = ''; // Clear existing list
        if (ownedPerfumes.length === 0) {
            const emptyMessage = document.createElement('li');
            emptyMessage.textContent = 'No perfumes added yet.';
            emptyMessage.style.textAlign = 'center';
            emptyMessage.style.fontStyle = 'italic';
            emptyMessage.style.color = '#777';
            perfumeList.appendChild(emptyMessage);
            return;
        }

        ownedPerfumes.forEach(perfume => {
            const listItem = document.createElement('li');
            listItem.setAttribute('data-id', perfume.id); // Store ID for actions
            listItem.innerHTML = `
                <span>${perfume.name}</span>
                <div class="perfume-actions">
                    <button class="button edit-button" data-id="${perfume.id}">
                        <span>EDIT</span>
                    </button>
                    <button class="button remove-button" data-id="${perfume.id}">
                        <span>DELETE</span>
                    </button>
                </div>
            `;
            perfumeList.appendChild(listItem);
        });
    }

    function addPerfume() {
        const perfumeName = perfumeNameInput.value.trim();
        if (perfumeName) {
            // Check if perfume already exists to prevent duplicates (case-insensitive)
            const exists = ownedPerfumes.some(p => p.name.toLowerCase() === perfumeName.toLowerCase());
            if (exists) {
                alert('This perfume is already in your list!');
                perfumeNameInput.value = '';
                return;
            }

            const newPerfume = {
                // In a real app, the ID would be generated by the backend
                id: `p${Date.now()}`, // Simple unique ID for frontend display
                name: perfumeName
            };
            ownedPerfumes.push(newPerfume);
            renderPerfumeList(); // Re-render the list to show the new item and its buttons
            perfumeNameInput.value = ''; // Clear input

            fetch('/api/perfumes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Authorization header might be needed if you implement token auth later
                },
                body: JSON.stringify({ perfumeName: newPerfume.name }) // Send newPerfume.name
            })
            .then(response => response.json().then(data => ({status: response.status, body: data})))
            .then(({status, body}) => {
                if (status === 201) {
                    console.log('Perfume added to backend:', body.perfumes);
                    // Optionally, update the local 'ownedPerfumes' with data from backend if IDs change
                    // For now, local update is sufficient as backend confirms add.
                } else {
                    alert('Error adding perfume to backend: ' + (body.message || 'Unknown error'));
                    // Optionally, remove the perfume from the local 'ownedPerfumes' list if backend failed
                    // ownedPerfumes = ownedPerfumes.filter(p => p.id !== newPerfume.id);
                    // renderPerfumeList();
                }
            })
            .catch(error => {
                console.error('Error adding perfume to backend:', error);
                alert('Could not save perfume. Please try again.');
                // ownedPerfumes = ownedPerfumes.filter(p => p.id !== newPerfume.id);
                // renderPerfumeList();
            });
        } else {
            alert('Please enter a perfume name.');
        }
    }

    function removePerfume(id) {
        const confirmed = confirm('Are you sure you want to remove this perfume?');
        if (confirmed) {
            ownedPerfumes = ownedPerfumes.filter(perfume => perfume.id !== id);
            renderPerfumeList();

            // --- Backend Communication Placeholder ---
            console.log('Sending request to remove perfume from backend:', id);
            /*
            fetch(`/api/perfumes/owned/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': 'Bearer YOUR_AUTH_TOKEN'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to remove perfume');
                }
                console.log('Perfume removed successfully from backend.');
            })
            .catch(error => {
                console.error('Error removing perfume:', error);
                alert('Could not remove perfume. Please try again.');
                // Optionally re-add to ownedPerfumes if backend failed
            });
            */
        }
    }

    function editPerfume(id, currentName) {
        const newName = prompt(`Edit perfume name for "${currentName}":`, currentName);
        if (newName !== null && newName.trim() !== '' && newName.trim() !== currentName.trim()) {
            // Check for duplicates before updating
            const exists = ownedPerfumes.some(p => p.name.toLowerCase() === newName.trim().toLowerCase() && p.id !== id);
            if (exists) {
                alert('This perfume name already exists in your list!');
                return;
            }

            const perfumeToUpdate = ownedPerfumes.find(p => p.id === id);
            if (perfumeToUpdate) {
                perfumeToUpdate.name = newName.trim();
                renderPerfumeList(); // Re-render to show updated name

                // --- Backend Communication Placeholder ---
                console.log('Sending request to update perfume on backend:', perfumeToUpdate);
                /*
                fetch(`/api/perfumes/owned/${id}`, {
                    method: 'PUT', // or PATCH
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer YOUR_AUTH_TOKEN'
                    },
                    body: JSON.stringify({ name: newName.trim() })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to update perfume');
                    }
                    console.log('Perfume updated successfully on backend.');
                })
                .catch(error => {
                    console.error('Error updating perfume:', error);
                    alert('Could not update perfume. Please try again.');
                    // Optionally revert name if backend failed
                });
                */
            }
        } else if (newName === null) {
            // User cancelled the prompt
        } else {
            alert('Perfume name cannot be empty.');
        }
    }

    // Event Listeners
    addPerfumeBtn.addEventListener('click', addPerfume);
    perfumeNameInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default form submission if input is in a form
            addPerfume();
        }
    });

    // Delegated event listener for edit/remove buttons within the list
    perfumeList.addEventListener('click', (event) => {
        const target = event.target;
        const listItem = target.closest('li'); // Find the closest parent <li>
        if (!listItem) return; // Click wasn't inside a list item

        // Ensure the click was on one of the buttons or their span children
        const clickedButton = target.closest('.button');
        if (!clickedButton) return; // Not a button

        const perfumeId = listItem.getAttribute('data-id'); // Get ID from the list item

        if (clickedButton.classList.contains('remove-button')) {
            removePerfume(perfumeId);
        } else if (clickedButton.classList.contains('edit-button')) {
            const currentName = listItem.querySelector('span').textContent; // Get the perfume name
            editPerfume(perfumeId, currentName);
        }
    });

    goToChatbotBtn.addEventListener('click', () => {
        fetch('/api/user/complete_first_login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json().then(data => ({status: response.status, body: data})))
        .then(({status, body}) => {
            if (status === 200) {
                alert(body.message || 'Setup complete! Taking you to the chatbot.');
                if (body.redirect_url) {
                    window.location.href = body.redirect_url;
                } else {
                    window.location.href = '/chatbot.html'; // Fallback
                }
            } else {
                alert('Error completing setup: ' + (body.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error completing first login setup:', error);
            alert('An error occurred. Please try again.');
        });
    });

    // Initial render when the page loads
    renderPerfumeList(); // Call this to display any initial perfumes (if ownedPerfumes had any)
});

document.addEventListener('DOMContentLoaded', () => {
    const editProfileForm = document.getElementById('editProfileForm');
    const changePasswordForm = document.getElementById('changePasswordForm');
    const signOutBtn = document.getElementById('signOutBtn');
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');

    // Profile Edit Fields
    const editAge = document.getElementById('editAge');
    const editWeight = document.getElementById('editWeight');
    const editHeight = document.getElementById('editHeight');
    const editSex = document.getElementById('editSex');
    const editStyle = document.getElementById('editStyle');
    const editRace = document.getElementById('editRace');

    // Password Change Fields
    const currentPassword = document.getElementById('currentPassword');
    const newPassword = document.getElementById('newPassword');
    const confirmNewPassword = document.getElementById('confirmNewPassword');

    // Error messages (re-use from previous sections)
    const editAgeError = document.getElementById('editAgeError');
    const editWeightError = document.getElementById('editWeightError');
    const editHeightError = document.getElementById('editHeightError');
    const editSexError = document.getElementById('editSexError');
    const editStyleError = document.getElementById('editStyleError');
    const editRaceError = document.getElementById('editRaceError');
    const currentPasswordError = document.getElementById('currentPasswordError');
    const newPasswordError = document.getElementById('newPasswordError');
    const confirmNewPasswordError = document.getElementById('confirmNewPasswordError');

    function displayError(element, message) {
        element.textContent = message;
    }

    function clearError(element) {
        element.textContent = '';
    }

    function validatePasswordStrength(password) {
        // At least 8 characters, one uppercase, one lowercase, one number, one special character
        const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$/;
        return re.test(password);
    }

    // --- Simulate fetching current user data for profile fields ---
    // In a real app, you'd fetch this from your backend when the page loads
    const mockUserData = {
        age: 30,
        weight: 70.5,
        height: 175,
        sex: 'female',
        style: 'classic',
        race: 'white'
    };

    function loadUserProfile() {
        if (editProfileForm) { // Ensure elements exist
            editAge.value = mockUserData.age;
            editWeight.value = mockUserData.weight;
            editHeight.value = mockUserData.height;
            editSex.value = mockUserData.sex;
            editStyle.value = mockUserData.style;
            editRace.value = mockUserData.race;
        }
    }

    // --- Event Listeners ---

    if (editProfileForm) {
        loadUserProfile(); // Load data on page load

        editProfileForm.addEventListener('submit', (event) => {
            event.preventDefault();
            let isValid = true;

            // Simple presence/range validation for profile fields
            if (editAge.value === '' || editAge.value < 13 || editAge.value > 120) {
                displayError(editAgeError, 'Please enter a valid age (13-120).'); isValid = false;
            } else { clearError(editAgeError); }
            if (editWeight.value === '' || editWeight.value < 20) {
                displayError(editWeightError, 'Please enter a valid weight (min 20kg).'); isValid = false;
            } else { clearError(editWeightError); }
            if (editHeight.value === '' || editHeight.value < 50) {
                displayError(editHeightError, 'Please enter a valid height (min 50cm).'); isValid = false;
            } else { clearError(editHeightError); }
            if (editSex.value === '') {
                displayError(editSexError, 'Please select your biological sex.'); isValid = false;
            } else { clearError(editSexError); }
            if (editStyle.value === '') {
                displayError(editStyleError, 'Please select your personal style.'); isValid = false;
            } else { clearError(editStyleError); }
            if (editRace.value === '') {
                displayError(editRaceError, 'Please select your racial group.'); isValid = false;
            } else { clearError(editRaceError); }

            if (isValid) {
                const updatedUserData = {
                    age: editAge.value,
                    weight: editWeight.value,
                    height: editHeight.value,
                    sex: editSex.value,
                    style: editStyle.value,
                    race: editRace.value
                };
                console.log('Updating profile with:', updatedUserData);
                // --- Backend API Call for Profile Update ---
                /*
                fetch('/api/user/profile', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer YOUR_AUTH_TOKEN' },
                    body: JSON.stringify(updatedUserData)
                })
                .then(response => {
                    if (!response.ok) throw new Error('Failed to update profile');
                    return response.json();
                })
                .then(data => {
                    alert('Profile updated successfully!');
                    console.log('Profile update response:', data);
                })
                .catch(error => {
                    console.error('Error updating profile:', error);
                    alert('Error updating profile. Please try again.');
                });
                */
                alert('Profile updated (simulated)!');
            }
        });
    }

    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', (event) => {
            event.preventDefault();
            let isValid = true;

            // Validate current password (should be checked against backend)
            if (currentPassword.value.trim() === '') {
                displayError(currentPasswordError, 'Current password is required.');
                isValid = false;
            } else {
                clearError(currentPasswordError);
            }

            // Validate new password strength
            if (!validatePasswordStrength(newPassword.value)) {
                displayError(newPasswordError, 'New password must be at least 8 characters, with uppercase, lowercase, number, and special character.');
                isValid = false;
            } else {
                clearError(newPasswordError);
            }

            // Validate new password confirmation
            if (newPassword.value !== confirmNewPassword.value) {
                displayError(confirmNewPasswordError, 'New passwords do not match.');
                isValid = false;
            } else {
                clearError(confirmNewPasswordError);
            }

            if (isValid) {
                console.log('Changing password...');
                // --- Backend API Call for Password Change ---
                /*
                fetch('/api/user/password', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer YOUR_AUTH_TOKEN' },
                    body: JSON.stringify({
                        currentPassword: currentPassword.value,
                        newPassword: newPassword.value
                    })
                })
                .then(response => {
                    if (!response.ok) throw new Error('Failed to change password');
                    alert('Password changed successfully!');
                    changePasswordForm.reset(); // Clear fields
                })
                .catch(error => {
                    console.error('Error changing password:', error);
                    alert('Error changing password. Please check your current password and try again.');
                });
                */
                alert('Password changed (simulated)!');
                changePasswordForm.reset();
            }
        });
    }


    if (signOutBtn) {
        signOutBtn.addEventListener('click', () => {
            const confirmed = confirm('Are you sure you want to sign out?');
            if (confirmed) {
                console.log('Signing out...');
                // --- Backend API Call for Logout ---
                /*
                fetch('/api/logout', { method: 'POST' })
                    .then(response => {
                        if (!response.ok) throw new Error('Logout failed');
                        // Clear local storage/session storage related to user session
                        localStorage.clear();
                        sessionStorage.clear();
                        alert('You have been signed out.');
                        window.location.href = 'index.html'; // Redirect to login page
                    })
                    .catch(error => {
                        console.error('Error during logout:', error);
                        alert('Could not sign out completely. Please try again.');
                    });
                */
                localStorage.clear();
                sessionStorage.clear();
                alert('You have been signed out (simulated).');
                window.location.href = 'index.html'; // Redirect to login
            }
        });
    }

    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', () => {
            const confirmed = confirm('WARNING: Are you absolutely sure you want to delete your account? This action cannot be undone.');
            if (confirmed) {
                console.log('Deleting account...');
                // --- Backend API Call for Account Deletion ---
                /*
                fetch('/api/user', {
                    method: 'DELETE',
                    headers: { 'Authorization': 'Bearer YOUR_AUTH_TOKEN' }
                })
                .then(response => {
                    if (!response.ok) throw new Error('Account deletion failed');
                    // Clear local storage/session storage
                    localStorage.clear();
                    sessionStorage.clear();
                    alert('Your account has been deleted successfully.');
                    window.location.href = 'index.html'; // Redirect to login page
                })
                .catch(error => {
                    console.error('Error deleting account:', error);
                    alert('Could not delete account. Please try again.');
                });
                */
                alert('Your account has been deleted (simulated).');
                localStorage.clear();
                sessionStorage.clear();
                window.location.href = 'index.html'; // Redirect to login
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chatHistory');
    const userMessageInput = document.getElementById('userMessageInput');
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    const quickReplyBtns = document.querySelectorAll('.quick-reply-btn');
    const typingIndicator = document.getElementById('typingIndicator');

    // Function to add a message to the chat history
    function addMessageToChat(messageText, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = messageText;
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to bottom
    }

    // Function to simulate sending message to backend and getting response
    async function sendMessage() {
        const messageText = userMessageInput.value.trim();
        if (messageText === '') return;

        addMessageToChat(messageText, 'user');
        userMessageInput.value = ''; // Clear input

        typingIndicator.style.display = 'block'; // Show typing indicator

        try {
            // --- Backend API Call for Chatbot ---
            // Replace with your actual chatbot API endpoint
            /*
            const response = await fetch('/api/chatbot/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer YOUR_AUTH_TOKEN' // If authenticated
                },
                body: JSON.stringify({ message: messageText, user_id: 'current_user_id' }) // Pass user ID
            });

            if (!response.ok) {
                throw new Error('Chatbot API network response was not ok');
            }

            const data = await response.json();
            const botResponse = data.response; // Assuming response has a 'response' field
            */
            // Simulate AI response delay
            await new Promise(resolve => setTimeout(resolve, 1500));
            let botResponse;

            // Simple conditional response for demonstration
            if (messageText.toLowerCase().includes('layering advice')) {
                botResponse = "For layering, start with a light base, then add a heavier scent. Consider complementing notes like vanilla with citrus, or woody notes with amber. Always test on a small area first!";
            } else if (messageText.toLowerCase().includes('new perfume') && messageText.toLowerCase().includes('date night')) {
                botResponse = "For a date night, I'd recommend something warm and inviting. Perhaps a gourmand scent with vanilla and caramel, or a seductive oriental with amber and spices. Do you have any preferred scent families or a price range?";
            } else if (messageText.toLowerCase().includes('fashion advice')) {
                botResponse = "Fashion advice? I'd love to help! Based on your style, a classic outfit with a statement accessory could elevate your look. What kind of occasion are you dressing for, or what pieces are you considering?";
            } else {
                botResponse = "Hmm, that's an interesting question! I'm still learning, but I can help with perfume recommendations, layering advice, and fashion tips. What else would you like to know?";
            }


            addMessageToChat(botResponse, 'bot');

        } catch (error) {
            console.error('Error communicating with chatbot:', error);
            addMessageToChat("I apologize, but I'm currently unable to process your request. Please try again later.", 'bot');
        } finally {
            typingIndicator.style.display = 'none'; // Hide typing indicator
        }
    }

    // Event Listeners for message input and send button
    sendMessageBtn.addEventListener('click', sendMessage);
    userMessageInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Event Listeners for quick replies
    quickReplyBtns.forEach(button => {
        button.addEventListener('click', () => {
            userMessageInput.value = button.getAttribute('data-message');
            sendMessage();
        });
    });
});


//wahala

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('actualSignupForm');
    if (form) { // Ensure we are on the signup page
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;

            // Basic validation
            if (!email || !password) {
                alert('Please enter both email and password.');
                return;
            }

            fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email, password: password }),
            })
            .then(response => response.json().then(data => ({ status: response.status, body: data })))
            .then(({ status, body }) => {
                if (status === 201) {
                    if (body.redirect_url) {
                        window.location.href = body.redirect_url;
                    } else {
                        // Fallback if redirect_url is missing, though backend should always send it
                        alert(body.message || 'Signup successful! Redirecting...');
                        window.location.href = '/login.html'; // Or a default page
                    }
                } else {
                    alert('Signup failed: ' + (body.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Signup error:', error);
                alert('An error occurred during signup. Please try again.');
            });
        });
    }
});