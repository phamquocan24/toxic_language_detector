export default {
    data() {
        return {
            isLeftColumnSectionDragging: false,
            isRightColumnSectionDragging: false,
            formLeftSections: [],
            formRightSections: [],
        };
    },

    computed: {
        storeFormSections() {
            return {
                get: (sortable) => {
                    return this.getSectionOrder(sortable.options.dataName);
                },
                set: (sortable) => {
                    return this.setSectionOrder(sortable);
                },
            };
        },
    },

    created() {
        this.formLeftSections = this.getSectionOrder(
            "product-form-left-sections"
        );
        this.formRightSections = this.getSectionOrder(
            "product-form-right-sections"
        );
    },

    methods: {
        getDefaultSectionOrder(key) {
            return {
                "product-form-left-sections": [
                    "variations",
                    "variants",
                ],
                "product-form-right-sections": [
                    "price",
                    "inventory",
                    "media",
                    "additional",
                ],
            }[key];
        },

        getSectionOrder(key) {
            const sectionsOrder = JSON.parse(localStorage.getItem(key));

            return sectionsOrder === null
                ? this.getDefaultSectionOrder(key)
                : sectionsOrder;
        },

        setSectionOrder(sortable) {
            this.$nextTick(() => {
                localStorage.setItem(
                    sortable.options.dataName,
                    JSON.stringify(sortable.toArray())
                );
            });
        },

        notifySectionOrderChange() {
            toaster(trans("product::products.section.order_saved"), {
                type: "default",
            });

            this.$nextTick(() => {
                this.initColorPicker();
            });
        },
    },
};
