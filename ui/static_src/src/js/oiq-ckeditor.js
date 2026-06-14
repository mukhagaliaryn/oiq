import katex from "katex";
import "katex/dist/katex.min.css";

window.katex = katex;

import ClassicEditor from "@ckeditor/ckeditor5-editor-classic/src/classiceditor";

import Essentials from "@ckeditor/ckeditor5-essentials/src/essentials";
import Paragraph from "@ckeditor/ckeditor5-paragraph/src/paragraph";
import Heading from "@ckeditor/ckeditor5-heading/src/heading";

import Bold from "@ckeditor/ckeditor5-basic-styles/src/bold";
import Italic from "@ckeditor/ckeditor5-basic-styles/src/italic";
import Underline from "@ckeditor/ckeditor5-basic-styles/src/underline";
import Strikethrough from "@ckeditor/ckeditor5-basic-styles/src/strikethrough";

import Link from "@ckeditor/ckeditor5-link/src/link";
import List from "@ckeditor/ckeditor5-list/src/list";
import BlockQuote from "@ckeditor/ckeditor5-block-quote/src/blockquote";
import CodeBlock from "@ckeditor/ckeditor5-code-block/src/codeblock";

import Table from "@ckeditor/ckeditor5-table/src/table";
import TableToolbar from "@ckeditor/ckeditor5-table/src/tabletoolbar";

import Image from "@ckeditor/ckeditor5-image/src/image";
import ImageUpload from "@ckeditor/ckeditor5-image/src/imageupload";
import ImageToolbar from "@ckeditor/ckeditor5-image/src/imagetoolbar";
import ImageCaption from "@ckeditor/ckeditor5-image/src/imagecaption";
import ImageStyle from "@ckeditor/ckeditor5-image/src/imagestyle";
import ImageResize from "@ckeditor/ckeditor5-image/src/imageresize";

import SimpleUploadAdapter from "@ckeditor/ckeditor5-upload/src/adapters/simpleuploadadapter";

import Math from "@isaul32/ckeditor5-math/src/math";
import AutoformatMath from "@isaul32/ckeditor5-math/src/autoformatmath";
import Autoformat from "@ckeditor/ckeditor5-autoformat/src/autoformat";

import "ckeditor5/ckeditor5.css";

function getCookie(name) {
    const match = document.cookie.match(
        new RegExp("(^|;\\s*)" + name + "=([^;]*)")
    );

    return match ? decodeURIComponent(match[2]) : null;
}

window.OIQEditor = {
    create(element) {
        return ClassicEditor.create(element, {
            plugins: [
                Essentials,
                Paragraph,
                Heading,
                Bold,
                Italic,
                Underline,
                Strikethrough,
                Link,
                List,
                BlockQuote,
                CodeBlock,
                Table,
                TableToolbar,
                Image,
                ImageUpload,
                ImageToolbar,
                ImageCaption,
                ImageStyle,
                ImageResize,
                SimpleUploadAdapter,
                Math,
                Autoformat,
                AutoformatMath,
            ],
            toolbar: [
                "undo",
                "redo",
                "|",
                "heading",
                "|",
                "bold",
                "italic",
                "underline",
                "strikethrough",
                "|",
                "bulletedList",
                "numberedList",
                "|",
                "insertTable",
                "link",
                "blockQuote",
                "codeBlock",
                "|",
                "imageUpload",
                "math",
            ],
            image: {
                toolbar: [
                    "imageStyle:inline",
                    "imageStyle:wrapText",
                    "imageStyle:breakText",
                    "|",
                    "resizeImage",
                    "|",
                    "imageTextAlternative",
                    "toggleImageCaption",
                ],
                resizeUnit: "px",
            },
            simpleUpload: {
                uploadUrl: element.dataset.oiqEditorUploadUrl,
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            },
            math: {
                engine: "katex",
                outputType: "span",
                forceOutputType: true,
                enablePreview: false,
                className: "math-tex",
                katexRenderOptions: {
                    throwOnError: false,
                },
            }
        }).then(function (editor) {
            if (element.dataset.oiqEditorHeight) {
                editor.editing.view.change(function (writer) {
                    writer.setStyle(
                        "min-height",
                        element.dataset.oiqEditorHeight,
                        editor.editing.view.document.getRoot()
                    );
                });
            }

            if (element.dataset.oiqEditorWidth) {
                editor.ui.view.element.style.width = element.dataset.oiqEditorWidth;
                editor.ui.view.element.style.maxWidth = "100%";
            }

            return editor;
        });
    },
};

function initEditor(element) {
    if (element.dataset.ckeditorInitialized === "true") {
        return;
    }

    element.dataset.ckeditorInitialized = "true";

    window.OIQEditor.create(element).catch(function (error) {
        console.error(error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-oiq-editor]").forEach(function (element) {
        // Django admin-нің "empty-form" қалыбы — жасырын үлгі, жаңа inline
        // жол қосылғанда осыдан клондалады, сондықтан мұнда CKEditor
        // инициализацияламаймыз (formset:added оқиғасында жасалады).
        if (element.closest(".empty-form")) {
            return;
        }

        initEditor(element);
    });
});

document.addEventListener("formset:added", function (event) {
    const row = event.target;

    if (!(row instanceof Element)) {
        return;
    }

    row.querySelectorAll("[data-oiq-editor]").forEach(initEditor);
});