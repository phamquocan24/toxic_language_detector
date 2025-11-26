import Vue from "vue";
import Errors from "@admin/js/Errors";
import axios from "axios";

Vue.prototype.route = route;

new Vue({
    el: "#app",

    data: {
        form: {
            first_name: "",
            last_name: "",
            email: "",
            password: "",
            password_confirmation: "",
            role: "",
            redirect_after_save: "0",
        },
        errors: new Errors(),
        submitting: false,
    },

    methods: {
        setFormDefaultData() {
            this.form = {
                first_name: "",
                last_name: "",
                email: "",
                password: "",
                password_confirmation: "",
                role: "",
                redirect_after_save: "0",
            };
            this.errors.clear();
        },

        resetForm() {
            this.setFormDefaultData();
            this.$nextTick(() => {
                document.querySelector("#first_name").focus();
            });
        },

        submit({ submissionType }) {
            this.form.redirect_after_save = submissionType === "save-exit" ? "1" : "0";
            this.submitting = true;
            this.errors.clear();

            axios
                .post(route("admin.users.store"), this.form)
                .then((response) => {
                    this.submitting = false;
                    if (this.form.redirect_after_save === "1") {
                        window.location.href = route("admin.users.index");
                    }
                })
                .catch((error) => {
                    this.submitting = false;
                    if (error.response && error.response.status === 422) {
                        this.errors.record(error.response.data.errors);
                    } else {
                        alert("An error occurred. Please try again.");
                    }
                });
        },
    },

    created() {
        this.setFormDefaultData();
    },
});
