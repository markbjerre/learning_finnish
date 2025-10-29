import { useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Sparkles, Trash2 } from "lucide-react";

// Mock data - will be replaced with actual database data
const mockWordDetail = {
  id: "1",
  word: "talo",
  translation: "hus",
  category: "substantiv",
  forms: {
    nominative: "talo",
    genitive: "talon",
    partitive: "taloa",
    illative: "taloon",
  },
  example: "Minun talo on suuri ja kaunis.",
  exampleTranslation: "Mit hus er stort og smukt.",
  memoryAid: "Tænk på 'talo' som et 'tårn af love' - et hus med mange regler!",
  addedAt: "2024-01-15"
};

const WordDetail = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  // TODO: Fetch actual word data from database using id

  const handleDelete = () => {
    // TODO: Implement delete functionality
    navigate('/wordlist');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button variant="ghost" size="sm" onClick={() => navigate('/wordlist')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Tilbage til listen
            </Button>
            <Button variant="destructive" size="sm" onClick={handleDelete}>
              <Trash2 className="h-4 w-4 mr-2" />
              Slet
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="shadow-[var(--shadow-medium)] border-0">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-4xl mb-2">{mockWordDetail.word}</CardTitle>
                <CardDescription className="text-xl">{mockWordDetail.translation}</CardDescription>
              </div>
              <Badge variant="secondary" className="text-sm">
                {mockWordDetail.category}
              </Badge>
            </div>
            <div className="text-xs text-muted-foreground mt-4">
              Tilføjet til din liste {new Date(mockWordDetail.addedAt).toLocaleDateString('da-DK')}
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Word Forms */}
            <div>
              <h3 className="font-semibold text-lg mb-3 text-foreground">Ordformer</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Object.entries(mockWordDetail.forms).map(([form, value]) => (
                  <div key={form} className="bg-secondary/50 rounded-lg p-4">
                    <div className="text-xs text-muted-foreground mb-1 capitalize">{form}</div>
                    <div className="font-medium text-foreground text-lg">{value}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Example Sentence */}
            <div>
              <h3 className="font-semibold text-lg mb-3 text-foreground">Eksempel</h3>
              <div className="space-y-2">
                <p className="text-foreground bg-secondary/30 p-4 rounded-lg italic text-lg">
                  {mockWordDetail.example}
                </p>
                <p className="text-muted-foreground pl-4">
                  → {mockWordDetail.exampleTranslation}
                </p>
              </div>
            </div>

            {/* Memory Aid */}
            <div>
              <h3 className="font-semibold text-lg mb-3 text-foreground flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-accent" />
                Hukommelsestip
              </h3>
              <p className="text-foreground bg-accent/10 border border-accent/20 p-4 rounded-lg">
                {mockWordDetail.memoryAid}
              </p>
            </div>

            {/* Action Button */}
            <div className="pt-4">
              <Button variant="outline" className="w-full" onClick={() => navigate('/wordlist')}>
                Tilbage til ordliste
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default WordDetail;
