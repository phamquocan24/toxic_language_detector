import Vue from "vue";
import ProductMixin from "./mixins/ProductMixin";
import Errors from "@admin/js/Errors";
import { generateSlug } from "@admin/js/functions";

Vue.prototype.defaultCurrencySymbol = Ecommerce.defaultCurrencySymbol;
Vue.prototype.route = route;

new Vue({
    el: "#app",

    mixins: [ProductMixin],

    data: {
        formSubmissionType: null,
        form: {
            brand_id: "",
            tax_class_id: "",
            is_active: true,
            media: [],
            is_virtual: false,
            manage_stock: 0,
            in_stock: 1,
            special_price_type: "fixed",
            meta: {},
            attributes: [],
            downloads: [],
            variations: [],
            variants: [],
            options: [],
            slug: null,
        },
        errors: new Errors(),
        selectizeConfig: {
            plugins: ["remove_button"],
        },
        searchableSelectizeConfig: {},
        categoriesSelectizeConfig: {},
        flatPickrConfig: {
            mode: "single",
            enableTime: true,
            altInput: true,
        },
    },

    created() {
        this.setSearchableSelectizeConfig();
        this.setCategoriesSelectizeConfig();
    },

    methods: {
        setProductSlug(value) {
            this.form.slug = generateSlug(value);
        },

        setFormDefaultData() {
            this.form = {
                brand_id: "",
                tax_class_id: "",
                is_active: true,
                media: [],
                is_virtual: false,
                manage_stock: 0,
                in_stock: 1,
                special_price_type: "fixed",
                meta: {},
                attributes: [],
                downloads: [],
                variations: [],
                variants: [],
                options: [],
                slug: null,
            };
        },

        resetForm() {
            this.setFormDefaultData();
            this.textEditor.get("description").setContent("");
            this.textEditor.get("description").execCommand("mceCancel");
            this.resetBulkEditVariantFields();

            this.focusField({
                selector: "#name",
            });
        },

        submit({ submissionType }) {
            this.formSubmissionType = submissionType;
        },
    },
});
