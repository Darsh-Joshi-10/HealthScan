document.getElementById("patientForm").addEventListener("submit", async (event) => {
    event.preventDefault();  // Prevent page reload

    const formData = new FormData();
    formData.append("PatientName", document.getElementById("patientName").value);
    formData.append("DateOfBirth", document.getElementById("patientDOB").value);
    formData.append("Symptoms", document.getElementById("symptoms").value);
    formData.append("xray_image", document.getElementById("imageUpload").files[0]);

    try {
        const response = await fetch("/api/add_record", {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        if (response.ok) {
            alert("Record added successfully!");
        } else {
            alert(result.error || "Failed to add record");
        }
    } catch (error) {
        console.error("Error:", error);
        // alert("An error occurred while adding the record.");
    }
});
