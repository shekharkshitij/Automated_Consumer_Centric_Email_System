import axios from "axios";
import React, { useState } from "react";
import "../styles.css";

const ComplaintForm = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    product: "",
    issue: "",
  });

  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const errors = {};

    if (!formData.name.trim()) {
      errors.name = "Name is required.";
    }
    if (!formData.email.trim()) {
      errors.email = "Email is required.";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = "Invalid email format.";
    }
    if (!formData.phone.trim()) {
      errors.phone = "Phone number is required.";
    } else if (!/^\d{10}$/.test(formData.phone)) {
      errors.phone = "Phone number must be 10 digits.";
    }
    if (!formData.product.trim()) {
      errors.product = "Product details are required.";
    }
    if (!formData.issue.trim()) {
      errors.issue = "Issue description is required.";
    }

    setErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(false);

    if (!validate()) {
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:5000/send-complaint", formData);
      setMessage(response.data.message);
      setFormData({
        name: "",
        email: "",
        phone: "",
        product: "",
        issue: "",
      });
    } catch (err) {
      setMessage(
        err.response && err.response.data.error
          ? err.response.data.error
          : "An unexpected error occurred. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h1>Submit Your Complaint</h1>
      {message && (
        <p className={`message ${message.includes("error") ? "error-message" : "success-message"}`}>
          {message}
        </p>
      )}
      <form onSubmit={handleSubmit}>
        {/* Name Field */}
        <div className="form-group">
          <label htmlFor="name">Name:</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Enter your full name"
          />
          {errors.name && <p className="error">{errors.name}</p>}
        </div>

        {/* Email Field */}
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Enter your email address"
          />
          {errors.email && <p className="error">{errors.email}</p>}
        </div>

        {/* Phone Field */}
        <div className="form-group">
          <label htmlFor="phone">Phone Number:</label>
          <input
            type="tel"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="Enter your phone number"
          />
          {errors.phone && <p className="error">{errors.phone}</p>}
        </div>

        {/* Product Field */}
        <div className="form-group">
          <label htmlFor="product">Product Details:</label>
          <input
            type="text"
            id="product"
            name="product"
            value={formData.product}
            onChange={handleChange}
            placeholder="Enter product name or ID"
          />
          {errors.product && <p className="error">{errors.product}</p>}
        </div>

        {/* Issue Description */}
        <div className="form-group">
          <label htmlFor="issue">Issue Description:</label>
          <textarea
            id="issue"
            name="issue"
            value={formData.issue}
            onChange={handleChange}
            placeholder="Describe the issue you're facing"
          ></textarea>
          {errors.issue && <p className="error">{errors.issue}</p>}
        </div>

        {/* Submit Button */}
        <button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit Complaint"}
        </button>
      </form>
    </div>
  );
};

export default ComplaintForm;
