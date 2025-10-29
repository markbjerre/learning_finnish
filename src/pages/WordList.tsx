import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BookOpen, ArrowLeft, BookMarked } from "lucide-react";
import { Input } from "@/components/ui/input";

// Mock data - will be replaced with actual database data
const mockWords = [
  {
    id: "1",
    word: "talo",
    translation: "hus",
    category: "substantiv",
    addedAt: "2024-01-15"
  },
  {
    id: "2",
    word: "juosta",
    translation: "at løbe",
    category: "verbum",
    addedAt: "2024-01-14"
  },
  {
    id: "3",
    word: "kaunis",
    translation: "smuk",
    category: "adjektiv",
    addedAt: "2024-01-13"
  },
];

const WordList = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const categories = ["all", "substantiv", "verbum", "adjektiv"];
  
  const filteredWords = mockWords.filter(word => {
    const matchesSearch = word.word.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         word.translation.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "all" || word.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-2">
              <BookMarked className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold text-foreground">Min Ordliste</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Search and Filter */}
        <div className="mb-8 space-y-4">
          <Input
            type="text"
            placeholder="Søg i dine ord..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-md"
          />
          
          <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
            <TabsList>
              <TabsTrigger value="all">Alle</TabsTrigger>
              <TabsTrigger value="substantiv">Substantiver</TabsTrigger>
              <TabsTrigger value="verbum">Verber</TabsTrigger>
              <TabsTrigger value="adjektiv">Adjektiver</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Word List */}
        {filteredWords.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2">
            {filteredWords.map((word) => (
              <Card 
                key={word.id}
                className="hover:shadow-[var(--shadow-medium)] transition-all cursor-pointer border-0 shadow-[var(--shadow-soft)]"
                onClick={() => navigate(`/word/${word.id}`)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-2xl mb-1">{word.word}</CardTitle>
                      <CardDescription className="text-base">{word.translation}</CardDescription>
                    </div>
                    <Badge variant="secondary">
                      {word.category}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-xs text-muted-foreground">
                    Tilføjet {new Date(word.addedAt).toLocaleDateString('da-DK')}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-medium text-foreground mb-2">
              {searchTerm ? "Ingen ord fundet" : "Din ordliste er tom"}
            </h3>
            <p className="text-muted-foreground mb-6">
              {searchTerm 
                ? "Prøv at søge efter noget andet" 
                : "Begynd at søge efter ord og gem dem til din liste"}
            </p>
            {!searchTerm && (
              <Button variant="hero" onClick={() => navigate('/')}>
                Søg efter ord
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WordList;
