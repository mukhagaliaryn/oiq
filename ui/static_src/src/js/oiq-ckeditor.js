import {
    ClassicEditor,
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
    Base64UploadAdapter,
    Undo,
} from "ckeditor5";
import { Math } from "@isaul32/ckeditor5-math";
import "ckeditor5/ckeditor5.css";
import "katex/dist/katex.min.css";


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
                Base64UploadAdapter,
                Undo,
                Math,
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
            table: {
                contentToolbar: [
                    "tableColumn",
                    "tableRow",
                    "mergeTableCells",
                ],
            },
            image: {
                toolbar: [
                    "imageTextAlternative",
                    "toggleImageCaption",
                    "imageStyle:inline",
                    "imageStyle:block",
                    "imageStyle:side",
                ],
            },
            math: {
                engine: "katex",
                outputType: "script",
                forceOutputType: false,
                enablePreview: true,
            },
        });
    },
};

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-oiq-editor]").forEach(function (element) {
        window.OIQEditor.create(element).catch(function (error) {
            console.error(error);
        });
    });
});
