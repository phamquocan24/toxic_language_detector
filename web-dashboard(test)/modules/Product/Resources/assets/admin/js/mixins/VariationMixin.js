import Coloris from "@melloware/coloris";

export default {
    data() {
        return {
            globalVariationId: "",//globalVariationId: ID của biến thể toàn cục.
            addingGlobalVariation: false,//Cờ kiểm tra xem có đang thêm biến thể toàn cục không.
            variations: [],//variations: Danh sách biến thể của sản phẩm.
        };
    },

    computed: {
        isAddGlobalVariationDisabled() {
            return this.globalVariationId === "" || this.addingGlobalVariation;//Kiểm tra xem nút thêm biến thể toàn cục có bị vô hiệu hóa không.
        },

        isCollapsedVariationsAccordion() {
            return this.form.variations.every(
                ({ is_open }) => is_open === false//Kiểm tra xem tất cả các biến thể có đang bị đóng hay không.
            );
        },
    },
//Theo dõi sự thay đổi của form.variations, nếu danh sách rỗng thì tự động thêm một biến thể mới.
    watch: {
        "form.variations": {
            immediate: true,
            handler(newValue) {
                if (newValue.length === 0) {
                    this.addVariation({ preventFocus: true });
                }
            },
        },
    },

    mounted() {
        this.initColorPicker();//Khởi tạo bộ chọn màu.
        this.hideColorPicker();//Ẩn bộ chọn màu khi người dùng click ra ngoài
    },

    methods: {
        //Đặt trạng thái mặc định cho variations
        //Đặt thuộc tính is_open thành false cho tất cả biến thể.
        prepareVariations(variations) {
            variations.forEach((variation) => {
                this.$set(variation, "is_open", false);
            });
        },

        //Tạo UID mới cho các variations và values
        regenerateVariationsUid() {
            this.form.variations.forEach((variation) => {
                this.$set(variation, "uid", this.uid());

                variation.values.forEach((_, valueIndex) => {
                    this.$set(variation.values[valueIndex], "uid", this.uid());
                });
            });
        },

        //Sắp xếp lại variations
        reorderVariations() {
            this.generateVariants();
            this.notifyVariantsReordered();
        },

        //Sắp xếp lại giá trị trong variations
        reorderVariationValues() {
            this.generateVariants(true);
        },

        // Thêm một biến thể mới vào danh sách form.variations.
        addVariation({ preventFocus }) {
            const uid = this.uid();

            this.form.variations.push({
                uid,
                type: "",
                is_global: false,
                is_open: true,
                values: [
                    {
                        uid: this.uid(),
                        image: {
                            id: null,
                            path: null,
                        },
                    },
                ],
            });

            if (!preventFocus) {
                this.focusField({
                    selector: `#variations-${uid}-name`,
                });
            }
        },

        //Xóa biến thể khỏi danh sách.
        deleteVariation(index, uid) {
            this.form.variations.splice(index, 1);
            this.clearErrors({ name: "variations", uid });
            this.generateVariants();
        },

        //Cập nhật loại biến thể (text, color, image)
        changeVariationType(value, index, uid) {
            const variation = this.form.variations[index];

            if (value !== "" && variation.values.length === 1) {
                this.focusField({
                    selector: `#variations-${uid}-values-${variation.values[0].uid}-label`,
                });
            }

            if (value === "text") {
                variation.values.forEach((value) => {
                    this.errors.clear([
                        `variations.${uid}.values.${value.uid}.color`,
                        `variations.${uid}.values.${value.uid}.image`,
                    ]);
                });
            } else if (value === "color") {
                variation.values.forEach((value) => {
                    this.errors.clear(
                        `variations.${uid}.values.${value.uid}.image`
                    );
                });

                this.$nextTick(() => {
                    this.initColorPicker();
                });
            } else if (value === "image") {
                variation.values.forEach((value, valueIndex) => {
                    if (!value.image) {
                        this.$set(variation.values[valueIndex], "image", {
                            id: null,
                            path: null,
                        });
                    }
                });

                variation.values.forEach((value) => {
                    this.errors.clear(
                        `variations.${uid}.values.${value.uid}.color`
                    );
                });
            } else {
                this.clearValuesError(index, uid);
            }
        },

        chooseVariationImage(
            variationIndex,
            variationUid,
            valueIndex,
            valueUid
        ) {
            let picker = new MediaPicker({ type: "image" });

            picker.on("select", ({ id, path }) => {
                this.form.variations[variationIndex].values[valueIndex].image =
                    {
                        id: +id,
                        path,
                    };

                this.errors.clear(
                    `variations.${variationUid}.values.${valueUid}.image`
                );
            });
        },

        //Thêm một hàng giá trị mới vào biến thể
        addVariationRow(index, variationUid) {
            const valueUid = this.uid();

            this.form.variations[index].values.push({
                uid: valueUid,
                image: {
                    id: null,
                    path: null,
                },
            });

            this.$nextTick(() => {
                this.initColorPicker();

                $(
                    `#variations-${variationUid}-values-${valueUid}-label`
                ).trigger("focus");
            });
        },

        //Thêm hàng mới nếu cần và chuyển focus đến hàng tiếp theo
        //Chỉ chạy nếu ô nhập hiện tại không trống
        addVariationRowOnPressEnter(event, variationIndex, valueIndex) {
            const variation = this.form.variations[variationIndex];
            const values = variation.values;

            if (event.target.value === "") return;

            if (values.length - 1 === valueIndex) {
                this.addVariationRow(variationIndex, variation.uid);

                return;
            }

            if (valueIndex < values.length - 1) {
                $(
                    `#variations-${variation.uid}-values-${
                        values[valueIndex + 1].uid
                    }-label`
                ).trigger("focus");
            }
        },

        //Xóa một giá trị khỏi biến thể
        deleteVariationRow(variationIndex, variationUid, valueIndex, valueUid) {
            const variation = this.form.variations[variationIndex];

            variation.values.splice(valueIndex, 1);

            this.clearValueRowErrors({
                name: "variations",
                variationUid,
                valueUid,
            });

            if (variation.values.length === 0) {
                this.addVariationRow(variationIndex, variationUid);
            }

            this.generateVariants();
        },

        //Cập nhật màu sắc cho từng giá trị của biến thể
        /*
            Với mỗi giá trị (values[valueIndex]):

            Lấy color của giá trị đó.

            Cập nhật thuộc tính CSS color của phần tử tương ứng (elements[valueIndex].style.color = color).

            Nếu color không có giá trị (null hoặc undefined), sẽ gán "" để xóa màu.

        */
        updateColorThumbnails() {
            this.form.variations.forEach(({ uid, type, values }) => {
                if (type !== "color") return;

                const elements = document.querySelectorAll(
                    `.variation-${uid} .clr-field`
                );

                values.forEach(({ color }, valueIndex) => {
                    elements[valueIndex].style.color = color || "";
                });
            });
        },

        //khởi tạo bộ chọn màu (color picker) bằng thư viện Coloris

        initColorPicker() {
            Coloris.init();//khởi tạo thư viện Coloris

            Coloris({
                el: ".color-picker",//Áp dụng Coloris cho các phần tử có class .color-picker.
                alpha: false,//Không hỗ trợ độ trong suốt (alpha channel).
                rtl: Ecommerce.rtl,//Kích hoạt chế độ Right-To-Left (RTL) nếu Ecommerce.rtl là true (hữu ích cho ngôn ngữ như tiếng Ả Rập).
                theme: "large",//Sử dụng giao diện Coloris kích thước lớn.
                wrap: true,//Coloris bao bọc (wrap) đầu vào, nghĩa là giao diện color picker sẽ nằm ngay trong ô nhập.
                format: "hex",//Màu sắc sẽ hiển thị ở định dạng mã màu HEX (#RRGGBB).
                selectInput: true,//Cho phép người dùng nhập mã màu trực tiếp vào ô nhập.
                swatches: [
                    "#D01C1F",
                    "#3AA845",
                    "#118257",
                    "#0A33AE",
                    "#0D46A0",
                    "#000000",
                    "#5F4C3A",
                    "#726E6E",
                    "#F6D100",
                    "#C0E506",
                    "#FF540A",
                    "#C5A996",
                    "#4B80BE",
                    "#A1C3DA",
                    "#C8BFC2",
                    "#A9A270",
                ],//Cung cấp danh sách các màu sắc phổ biến để người dùng chọn nhanh.
            });
        },

        //được sử dụng để ẩn bảng chọn màu (color picker) của Coloris khi người dùng nhấn vào một màu trong bảng màu (swatches).
        /*
            Lắng nghe sự kiện "click" trên toàn bộ tài liệu (document).

            Chỉ kích hoạt khi người dùng click vào nút trong #clr-swatches, tức là các nút màu trong bảng màu nhanh của Coloris.
            Lấy phần tử cha (#clr-picker) của nút vừa click.
            Xóa class "clr-open" khỏi #clr-picker, làm cho bảng chọn màu bị đóng.
        */

        hideColorPicker() {
            $(document).on("click", "#clr-swatches button", (e) => {
                $(e.currentTarget)
                    .parents("#clr-picker")
                    .removeClass("clr-open");
            });
        },

        addGlobalVariation() {
            if (this.globalVariationId === "") return;
            this.addingGlobalVariation = true;

            $.ajax({
                type: "GET",
                url: route("admin.variations.show", { id: this.globalVariationId }),
                dataType: "json",
                success: (variation) => {
                    variation.uid = this.uid();
                    variation.is_open = true;

                    variation.values.forEach((value) => {
                        value.uid = this.uid();
                    });

                    this.form.variations.push(variation);
                    this.generateVariants();

                    this.$nextTick(() => {
                        $(`#variations-${variation.uid}-name`).trigger("focus");
                    });
                },
            })
                .catch((error) => {
                    toaster(error.responseJSON.message, {
                        type: "error",
                    });
                })
                .always(() => {
                    this.globalVariationId = "";
                    this.addingGlobalVariation = false;
                });
        },
    },
};
