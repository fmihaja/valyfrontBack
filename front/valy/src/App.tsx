import { Download, FileText, Search, Sheet } from "lucide-react";
import { Button } from "./components/ui/button";
import { ButtonGroup } from "./components/ui/button-group";
import { Input } from "./components/ui/input";
import { Separator } from "./components/ui/separator";
import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Spinner } from "./components/ui/spinner";

function App() {
    const nbPdf = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const [economie, setEconomie] = useState(false);
    const [pending, setPending] = useState(false);
    const refresh = () => {
        setPending(true);
        if (economie) {
            axios
                .post("http://localhost:8000/scrape/economie")
                .then((response) => { toast.success(response.data.message)} )
                .catch((error) => {toast.warning(error)})
                .finally(() => {
                    setPending(false);
                });
        } else {
            axios
                .post("http://localhost:8000/scrape/ecb")
                .then((response) => {toast.success(response.data.message)})
                .catch((error) => {toast.warning(error)})
                .finally(() => {
                    setPending(false);
                });
        }
    };
    return (
        <>
            <div className=" w-screen h-screen flex flex-col items-center p-5">
                <div className="w-full flex justify-end gap-5">
                    <Input
                        className="w-70"
                        type="text"
                        placeholder="Rechercher"
                    />
                    <ButtonGroup>
                        <Button variant="outline">
                            <Search /> Rechercher
                        </Button>
                        <Button variant="outline" onClick={()=>refresh()}>
                          {pending && <Spinner />}
                          Recharger</Button>
                    </ButtonGroup>
                </div>
                <div className="w-full h-full flex flex-col justify-center items-center gap-5">
                    <div className="w-full flex justify-center gap-30 mt-10">
                        <Button
                            className="w-25"
                            onClick={() => setEconomie(true)}
                            size="lg"
                            variant={economie ? "default" : "outline"}
                            disabled={pending}
                        >
                            Economie
                        </Button>
                        <Button
                            className="w-25"
                            onClick={() => setEconomie(false)}
                            size="lg"
                            disabled={pending}
                            variant={!economie ? "default" : "outline"}
                        >
                            Euro
                        </Button>
                    </div>
                    <div className="w-[70%] h-full flex flex-col items-center gap-3">
                        {economie && (
                            <div className="w-full flex felx-col">
                                <div className="w-full flex justify-between items-center px-3">
                                    <div className="w-1/2 flex items-center gap-5">
                                        <Sheet className="w-20 h-20 " />
                                        <h1 className="text-4xl">
                                            Excelle economie
                                        </h1>
                                    </div>
                                    {/* Lien de téléchargement */}
                                    <a
                                        href="/assets/economie/economic_calendar_sections.xlsx"
                                        download="economic_calendar_sections.xlsx"
                                        className="inline-flex items-center justify-center w-15 h-15 rounded-full hover:bg-accent hover:text-accent-foreground transition-colors"
                                    >
                                        <Download size={32} />
                                    </a>
                                </div>
                            </div>
                        )}
                        {!economie &&
                            nbPdf.map((num) => (
                                <div
                                    key={num}
                                    className="w-full flex flex-col border p-3 rounded-lg"
                                >
                                    <div className="w-full flex justify-between items-center px-3">
                                        <div className="w-1/2 flex items-center gap-5">
                                            <FileText className="w-20 h-20" />
                                            <h1 className="text-2xl">
                                                {num}.pdf
                                            </h1>
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

                        <Separator />
                    </div>
                </div>
            </div>
        </>
    );
}

export default App;
