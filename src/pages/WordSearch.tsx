import { useState } from "react";
import { Search, BookOpen, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";

const WordSearch = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [wordData, setWordData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    
    setIsLoading(true);
    // TODO: Integrate with AI API later
    // Mock data for now
    setTimeout(() => {
      setWordData({
        word: searchTerm,
        translation: "eksempel oversættelse",
        forms: {
          nominative: searchTerm,
          genitive: `${searchTerm}n`,
          partitive: `${searchTerm}a`,
          illative: `${searchTerm}an`,
        },
        example: `Tämä on esimerkki lause "${searchTerm}".`,
        wordHints: [
          { word: "Tämä", translation: "denne/dette" },
          { word: "esimerkki", translation: "eksempel" },
          { word: "lause", translation: "sætning" }
        ],
        memoryAid: "En sjov måde at huske dette ord på...",
        category: "substantiv"
      });
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold text-foreground">Suomi Oppija</h1>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={() => navigate('/wordlist')}>
              Min Ordliste
            </Button>
            <Button variant="outline" onClick={() => navigate('/auth')}>
              Log ind
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 bg-[image:var(--gradient-hero)]">
        <div className="container mx-auto max-w-3xl text-center">
          <div className="inline-flex items-center gap-2 bg-primary-foreground/10 backdrop-blur-sm px-4 py-2 rounded-full mb-6">
            <Sparkles className="h-4 w-4 text-primary-foreground" />
            <span className="text-sm font-medium text-primary-foreground">AI-drevet finsk læring</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
            Lær Finsk Med Lethed
          </h2>
          <p className="text-lg text-primary-foreground/90 mb-8">
            Slå ord op, få oversættelser, bøjninger og hukommelsestips med kunstig intelligens
          </p>
          
          {/* Search Bar */}
          <div className="flex gap-2 max-w-2xl mx-auto shadow-[var(--shadow-medium)]">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Indtast et finsk ord..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-10 h-14 text-lg bg-card border-0"
              />
            </div>
            <Button 
              variant="accent" 
              size="lg" 
              onClick={handleSearch}
              disabled={isLoading}
              className="h-14 px-8"
            >
              {isLoading ? "Søger..." : "Søg"}
            </Button>
          </div>
        </div>
      </section>

      {/* Results Section */}
      <section className="py-12 px-4">
        <div className="container mx-auto max-w-4xl">
          {wordData && (
            <Card className="shadow-[var(--shadow-medium)] border-0">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-3xl mb-2">{wordData.word}</CardTitle>
                    <CardDescription className="text-lg">{wordData.translation}</CardDescription>
                  </div>
                  <Badge variant="secondary" className="text-sm">
                    {wordData.category}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Word Forms */}
                <div>
                  <h3 className="font-semibold text-lg mb-3 text-foreground">Ordformer</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {Object.entries(wordData.forms).map(([form, value]) => (
                      <div key={form} className="bg-secondary/50 rounded-lg p-3">
                        <div className="text-xs text-muted-foreground mb-1 capitalize">{form}</div>
                        <div className="font-medium text-foreground">{value as string}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Example Sentence */}
                <div>
                  <h3 className="font-semibold text-lg mb-2 text-foreground">Eksempel</h3>
                  <p className="text-foreground/80 bg-secondary/30 p-4 rounded-lg italic">
                    {wordData.example}
                  </p>
                  
                  {/* Word Hints */}
                  {wordData.wordHints && wordData.wordHints.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-sm text-muted-foreground font-medium">Svære ord:</p>
                      <div className="flex flex-wrap gap-2">
                        {wordData.wordHints.map((hint: any, index: number) => (
                          <div 
                            key={index}
                            className="bg-card border border-border rounded-md px-3 py-1.5 text-sm"
                          >
                            <span className="font-medium text-foreground">{hint.word}</span>
                            <span className="text-muted-foreground"> → {hint.translation}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Memory Aid */}
                <div>
                  <h3 className="font-semibold text-lg mb-2 text-foreground flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-accent" />
                    Hukommelsestip
                  </h3>
                  <p className="text-foreground/80 bg-accent/10 border border-accent/20 p-4 rounded-lg">
                    {wordData.memoryAid}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <Button variant="hero" className="flex-1" onClick={() => navigate('/auth')}>
                    Gem til Min Liste
                  </Button>
                  <Button variant="outline" onClick={() => setWordData(null)}>
                    Ryd
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {!wordData && !isLoading && (
            <div className="text-center py-12">
              <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-medium text-foreground mb-2">Søg efter et finsk ord</h3>
              <p className="text-muted-foreground">
                Indtast et ord ovenfor for at få oversættelse, bøjninger og hukommelsestips
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default WordSearch;
