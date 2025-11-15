import { Download, FileText, Search, Sheet } from "lucide-react";
import { Button } from "./components/ui/button";
import { ButtonGroup } from "./components/ui/button-group";
import { Input } from "./components/ui/input";
import { Separator } from "./components/ui/separator";
import { useState } from "react";
import axios from "axios";
import { toast, Toaster } from "sonner";
import { Spinner } from "./components/ui/spinner";

function App() {
    const nbPdf = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const ip="localhost"
    const [selected, setSelected] =
        useState<"economie" | "euro" | "usa">("economie");
    const [pending, setPending] = useState(false);

    const refresh = () => {
        setPending(true);
        let endpoint = "";

        if (selected === "economie") {
            endpoint = `http://${ip}:8000/scrape/economie`;
        } else if (selected === "euro") {
            endpoint = `http://${ip}:8000/scrape/ecb`;
        } else if (selected === "usa") {
            endpoint = `http://${ip}:8000/scrape/usa`;
        }

        axios
            .post(endpoint)
            .then((response) => {
                toast.success(response.data.message);
            })
            .catch((error) => {
                toast.warning(error.message);
            })
            .finally(() => {
                setPending(false);
            });
    };

    return (
        <>
            <div className="w-screen h-screen flex flex-col items-center p-5">
                <div className="w-full flex justify-end gap-5">
                    <Input className="w-70" type="text" placeholder="Rechercher" />

                    <ButtonGroup>
                        <Button variant="outline">
                            <Search /> Rechercher
                        </Button>

                        <Button
                            variant="outline"
                            disabled={pending}
                            onClick={() => refresh()}
                        >
                            {pending && <Spinner />}
                            Recharger
                        </Button>
                    </ButtonGroup>
                </div>

                <div className="w-full h-full flex flex-col justify-center items-center gap-5">
                    <div className="w-full flex justify-center gap-5 mt-10">
                        <Button
                            className="w-25"
                            onClick={() => setSelected("economie")}
                            size="lg"
                            variant={selected === "economie" ? "default" : "outline"}
                            disabled={pending}
                        >
                            Economie
                        </Button>

                        <Button
                            className="w-25"
                            onClick={() => setSelected("euro")}
                            size="lg"
                            disabled={pending}
                            variant={selected === "euro" ? "default" : "outline"}
                        >
                            Euro
                        </Button>

                        <Button
                            className="w-25"
                            onClick={() => setSelected("usa")}
                            size="lg"
                            disabled={pending}
                            variant={selected === "usa" ? "default" : "outline"}
                        >
                            USA
                        </Button>
                    </div>

                    <div className="w-[70%] h-full flex flex-col items-center gap-3">

                        {/* ----- ÉCONOMIE ----- */}
                        {selected === "economie" && (
                            <div className="w-full flex flex-col">
                                <div className="w-full flex justify-between items-center px-3">
                                    <div className="w-1/2 flex items-center gap-5">
                                        <Sheet className="w-20 h-20" />
                                        <h1 className="text-4xl">Excel économie</h1>
                                    </div>

                                    <a
                                        href="/economie/economic_calendar_sections.xlsx"
                                        download="economic_calendar_sections.xlsx"
                                        className="inline-flex items-center justify-center w-15 h-15 rounded-full hover:bg-accent hover:text-accent-foreground transition-colors"
                                    >
                                        <Download size={32} />
                                    </a>
                                </div>
                            </div>
                        )}

                        {/* ----- EURO ----- */}
                        {selected === "euro" &&
                            nbPdf.map((num) => (
                                <div
                                    key={num}
                                    className="w-full flex flex-col border p-3 rounded-lg"
                                >
                                    <div className="w-full flex justify-between items-center px-3">
                                        <div className="w-1/2 flex items-center gap-5">
                                            <FileText className="w-20 h-20" />
                                            <h1 className="text-2xl">{num}.pdf</h1>
                                        </div>

                                        <a
                                            href={`/ecb_documents/${num}.pdf`}
                                            download={`${num}.pdf`}
                                            className="inline-flex items-center justify-center w-15 h-15 rounded-full hover:bg-accent hover:text-accent-foreground transition-colors"
                                        >
                                            <Download size={32} />
                                        </a>
                                    </div>
                                </div>
                            ))}

                        {/* ----- USA ----- */}
                        {selected === "usa" &&
                            nbPdf.map((num) => (
                                <div
                                    key={num}
                                    className="w-full flex flex-col border p-3 rounded-lg"
                                >
                                    <div className="w-full flex justify-between items-center px-3">
                                        <div className="w-1/2 flex items-center gap-5">
                                            <FileText className="w-20 h-20" />
                                            <h1 className="text-2xl">{num}.pdf</h1>
                                        </div>

                                        <a
                                            href={`/usa_documents/${num}.pdf`}
                                            download={`${num}.pdf`}
                                            className="inline-flex items-center justify-center w-15 h-15 rounded-full hover:bg-accent hover:text-accent-foreground transition-colors"
                                        >
                                            <Download size={32} />
                                        </a>
                                    </div>
                                </div>
                            ))}

                        <Separator />
                    </div>
                </div>

                <Toaster position="top-center" />
            </div>
        </>
    );
}

export default App;
