import Vue from "vue";
import ProductMixin from "./mixins/ProductMixin";
import Errors from "@admin/js/Errors";

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
        this.setFormData();
        this.setSearchableSelectizeConfig();
        this.setCategoriesSelectizeConfig();
        this.setDefaultVariantUid();
        this.setVariantsLength();
    },

    mounted() {
        this.hideAlertExitFlash();
    },

    methods: {
        prepareFormData(formData) {
            this.prepareAttributes(formData.attributes);
            this.prepareVariations(formData.variations);
            this.prepareVariants(formData.variants);
            this.prepareOptions(formData.options);

            return formData;
        },

        setFormData() {
            this.form = { ...this.prepareFormData(Ecommerce.data["product"]) };
        },

        setDefaultVariantUid() {
            if (this.hasAnyVariant) {
                this.defaultVariantUid = this.form.variants.find(
                    ({ is_default }) => is_default === true
                ).uid;
            }
        },

        setVariantsLength() {
            this.variantsLength = this.form.variants.length;
        },

        hideAlertExitFlash() {
            const alertExitFlash = $(".alert-exit-flash");

            if (alertExitFlash.length !== 0) {
                setTimeout(() => {
                    alertExitFlash.remove();
                }, 3000);
            }
        },

        submit({ submissionType }) {
            this.formSubmissionType = submissionType;
        },
    },
});
